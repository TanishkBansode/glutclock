from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from .. import config, storage


def _fetch_yfinance() -> pd.DataFrame:
    import yfinance as yf

    raw = yf.download(
        config.ALL_TICKERS,
        period=f"{config.MARKET_BACKFILL_DAYS}d",
        interval="1d",
        group_by="ticker",
        threads=True,
        progress=False,
        auto_adjust=False,
    )
    frames = []
    for symbol in config.ALL_TICKERS:
        try:
            sub = raw[symbol]
        except KeyError:
            continue
        if sub is None or sub.empty:
            continue
        closes = sub["Close"].dropna()
        if closes.empty:
            continue
        frames.append(
            pd.DataFrame(
                {
                    "date": closes.index.strftime(config.RUN_DATE_FMT),
                    "symbol": symbol,
                    "close": closes.values,
                }
            )
        )
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _stooq_symbol(symbol: str) -> str | None:
    s = symbol.lower()
    if s.startswith("^"):
        mapping = {"^sox": "^sox", "^ixic": "^ixic", "^ks11": "^ks11", "^tnx": "10usy.b"}
        return mapping.get(symbol)
    if "." not in s:
        return f"{s}.us"
    return s


def _fetch_stooq(symbols: list[str]) -> pd.DataFrame:
    import requests

    frames = []
    for symbol in symbols:
        ss = _stooq_symbol(symbol)
        if ss is None:
            continue
        url = f"https://stooq.com/q/d/l/?s={ss}&i=d"
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            from io import StringIO

            df = pd.read_csv(StringIO(resp.text))
        except Exception:
            continue
        if df.empty or "Close" not in df.columns:
            continue
        df = df.rename(columns={"Date": "date", "Close": "close"})
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime(config.RUN_DATE_FMT)
        df = df.dropna(subset=["date"])
        frames.append(pd.DataFrame({"date": df["date"], "symbol": symbol, "close": df["close"]}))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def run() -> int:
    today = datetime.now(timezone.utc).strftime(config.RUN_DATE_FMT)
    lake = storage.read_table("market_prices")
    known_dates = set(lake["date"].unique()) if lake is not None and not lake.empty else set()

    data = _fetch_yfinance()
    source = "yfinance"
    missing = [s for s in config.ALL_TICKERS]
    if data is not None and not data.empty:
        covered = set(data["symbol"].unique())
        missing = [s for s in config.ALL_TICKERS if s not in covered]
    fallback = _fetch_stooq(missing) if missing else pd.DataFrame()
    if not fallback.empty:
        data = pd.concat([data, fallback], ignore_index=True)
        source += "+stooq"
    if data is None or data.empty:
        storage.log_run("markets", "failed")
        return 0

    data["source"] = source
    data["ingested_at"] = today
    keys = ["symbol", "date"]
    total = storage.write_table(data, "market_prices", keys)
    new_days = len(set(data["date"]) - known_dates)
    storage.log_run("markets", "ok", rows=len(data),
                    detail=f"total={total} new_days={new_days} src={source}")
    return new_days


if __name__ == "__main__":
    run()
