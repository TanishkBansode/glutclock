from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

from .. import config, storage

_TAIPEI = timezone(timedelta(hours=8))
_CHANGE_RE = re.compile(r"([▲▼])\s*(-?\d+(?:\.\d+)?)\s*%")


def _session_date() -> str:
    return datetime.now(_TAIPEI).strftime(config.RUN_DATE_FMT)


def _parse_change(raw) -> float | None:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    m = _CHANGE_RE.search(str(raw))
    if not m:
        return None
    arrow, pct = m.group(1), float(m.group(2))
    return abs(pct) if arrow == "▲" else -abs(pct)


def fetch_page(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=config.TF_HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        storage.log_run("trendforce", "error", detail=f"{url}: {exc}"[:200])
        return None


def parse_price_table(html: str, tokens: list[str]):
    from io import StringIO

    tables = pd.read_html(StringIO(html))
    for table in tables:
        cols = [str(c) for c in table.columns]
        if "Item" not in cols or "Session Average" not in cols:
            continue
        items = table["Item"].astype(str)
        if tokens and not any(any(tok in it for tok in tokens) for it in items):
            continue
        return table
    return None


def ingest_series(series_name: str, spec: dict) -> pd.DataFrame:
    html = fetch_page(spec["url"])
    if html is None:
        return pd.DataFrame()
    table = parse_price_table(html, spec["tokens"])
    if table is None:
        storage.log_run("trendforce", "error", detail=f"{series_name}: no parsable table")
        return pd.DataFrame()
    rows = []
    date = _session_date()
    for _, r in table.iterrows():
        item = str(r["Item"]).strip()
        avg = pd.to_numeric(r.get("Session Average"), errors="coerce")
        if pd.isna(avg) or not item:
            continue
        rows.append(
            {
                "series": series_name,
                "item": item,
                "date": date,
                "session_avg": float(avg),
                "daily_high": pd.to_numeric(r.get("Daily High", r.get("Weekly High")), errors="coerce"),
                "daily_low": pd.to_numeric(r.get("Daily Low", r.get("Weekly Low")), errors="coerce"),
                "session_change_pct": _parse_change(r.get("Session Change")),
                "sanity_ok": True,
            }
        )
    return pd.DataFrame(rows)


def apply_sanity_gate(today: pd.DataFrame, lake: pd.DataFrame | None) -> pd.DataFrame:
    if today.empty or lake is None or lake.empty:
        return today
    prev = (
        lake.sort_values("date")
        .groupby(["series", "item"])
        .tail(1)[["series", "item", "session_avg"]]
        .rename(columns={"session_avg": "prev_avg"})
    )
    merged = today.merge(prev, on=["series", "item"], how="left")
    merged["prev_avg"] = pd.to_numeric(merged["prev_avg"], errors="coerce")
    jump = (merged["session_avg"] / merged["prev_avg"] - 1.0).abs() * 100.0
    merged["sanity_ok"] = ~(merged["prev_avg"].notna() & (jump > config.SANITY_PCT_LIMIT))
    return merged.drop(columns=["prev_avg"])


def run() -> int:
    frames = []
    for series_name, spec in config.TF_PRICE_PAGES.items():
        frames.append(ingest_series(series_name, spec))
    today = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    if today.empty:
        storage.log_run("trendforce", "failed")
        return 0
    lake = storage.read_table("physical_prices")
    today = apply_sanity_gate(today, lake)
    keys = ["series", "item", "date"]
    total = storage.write_table(today, "physical_prices", keys)
    flagged = int((~today["sanity_ok"]).sum())
    status = "ok_with_flags" if flagged else "ok"
    storage.log_run("trendforce", status, rows=len(today),
                    detail=f"flagged={flagged} total_rows={total}")
    return len(today)


if __name__ == "__main__":
    run()
