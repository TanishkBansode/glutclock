from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import config


def _path(name: str) -> Path:
    return config.LAKE_DIR / f"{name}.parquet"


def write_table(df: pd.DataFrame, name: str, keys: list[str]) -> int:
    config.LAKE_DIR.mkdir(parents=True, exist_ok=True)
    path = _path(name)
    if path.exists():
        old = pd.read_parquet(path)
        df = pd.concat([old, df], ignore_index=True)
        df = df.drop_duplicates(subset=keys, keep="last")
        df = df.sort_values(keys).reset_index(drop=True)
    df.to_parquet(path, index=False)
    return len(df)


def read_table(name: str) -> pd.DataFrame | None:
    path = _path(name)
    if not path.exists():
        return None
    return pd.read_parquet(path)


def sql(query: str):
    import duckdb

    con = duckdb.connect(str(config.DATA_DIR / "lake.duckdb"))
    try:
        return con.execute(query).fetchdf()
    finally:
        con.close()


def log_run(source: str, status: str, rows: int = 0, detail: str = "") -> None:
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source,
        "status": status,
        "rows": rows,
        "detail": detail,
    }
    with open(config.LOGS_DIR / "runs.jsonl", "a") as fh:
        fh.write(json.dumps(entry) + "\n")


def features_hash(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.md5(blob.encode()).hexdigest()[:12]


def append_ledger(record: dict) -> None:
    with open(config.LEDGER_PATH, "a") as fh:
        fh.write(json.dumps(record, default=str) + "\n")
