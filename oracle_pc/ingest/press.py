from __future__ import annotations

import json
import re

import pandas as pd
import requests

from .. import config, storage

_ARTICLE_RE = re.compile(r"/(?:presscenter/news|news)/(\d{8})[-\d]*\.html")
_FORECAST_RE = re.compile(
    r"(rise[sd]?|increase[sd]?|climb\w*|surge\w*|hike\w*|grow\w*|decline[sd]?|"
    r"drop\w*|fall\w*|decrease[sd]?)[^.<]{0,140}?(\d{1,3})\s*[–—-]\s*(\d{1,3})\s*%",
    re.IGNORECASE,
)
_QOQ_CONTEXT = re.compile(r"(QoQ|quarter|sequential)", re.IGNORECASE)
_MAX_NEW_ARTICLES = 12


def _list_articles() -> pd.DataFrame:
    from bs4 import BeautifulSoup

    rows = {}
    for page_url in (config.TF_PRESS_URL,):
        try:
            resp = requests.get(page_url, headers=config.TF_HEADERS, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as exc:
            storage.log_run("press", "error", detail=str(exc)[:200])
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.find_all("a", href=True):
            m = _ARTICLE_RE.search(a["href"])
            if not m:
                continue
            yyyymmdd = m.group(1)
            url = config.TF_BASE + (a["href"] if a["href"].startswith("/") else "/" + a["href"])
            title = a.get_text(strip=True)
            existing = rows.get(url)
            if existing is None or (len(title) > len(existing["title"])):
                rows[url] = {
                    "url": url,
                    "published": f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:]}",
                    "title": title,
                }
    return pd.DataFrame(list(rows.values()))


def _extract_forecasts(html: str) -> list[str]:
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    out = []
    for m in _FORECAST_RE.finditer(text):
        window = text[max(0, m.start() - 40) : m.end() + 40]
        if not _QOQ_CONTEXT.search(window):
            continue
        direction = "down" if m.group(1).lower().startswith(("declin", "drop", "fall", "decreas")) else "up"
        out.append(f"{m.group(2)}-{m.group(3)}%_{direction}")
    return sorted(set(out))


def _fetch_new(archive: pd.DataFrame | None) -> list[dict]:
    known = set(archive["url"]) if archive is not None and not archive.empty else set()
    listing = _list_articles()
    if listing.empty:
        return []
    listing = listing[~listing["url"].isin(known)]
    listing = listing[
        listing["title"].str.lower().str.contains("|".join(config.PRESS_KEYWORDS), na=False)
    ]
    listing = listing.sort_values("published", ascending=False).head(_MAX_NEW_ARTICLES)
    records = []
    for _, row in listing.iterrows():
        try:
            resp = requests.get(row["url"], headers=config.TF_HEADERS, timeout=30)
            resp.raise_for_status()
        except requests.RequestException:
            continue
        forecasts = _extract_forecasts(resp.text)
        records.append(
            {
                "url": row["url"],
                "published": row["published"],
                "title": row["title"][:300],
                "forecasts_json": json.dumps(forecasts),
                "is_memory": True,
            }
        )
    return records


def run() -> int:
    archive = storage.read_table("press_archive")
    records = _fetch_new(archive)
    if not records:
        storage.log_run("press", "empty")
        return 0
    total = storage.write_table(pd.DataFrame(records), "press_archive", ["url"])
    storage.log_run("press", "ok", rows=len(records), detail=f"total={total}")
    return len(records)


if __name__ == "__main__":
    run()
