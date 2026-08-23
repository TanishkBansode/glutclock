from __future__ import annotations

import pandas as pd

from .. import config, storage


def _seed_frame() -> pd.DataFrame:
    seed_rows = [
        ("2026-06-10", "D10", None, 205.8),
        ("2026-07-10", "D10", None, 193.1),
        ("2026-08-11", "D10", None, 155.4),
        ("2026-08-21", "D20", 26030.0, 198.8),
    ]
    return pd.DataFrame(
        seed_rows, columns=["period", "window_type", "exports_usd_mn", "yoy_pct"]
    )


def _load_manual() -> pd.DataFrame:
    if not config.KOREA_MANUAL_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(config.KOREA_MANUAL_CSV)
    missing = [c for c in config.KOREA_SCHEMA if c not in df.columns]
    if missing:
        storage.log_run("korea_customs", "error", detail=f"bad schema, missing={missing}")
        return pd.DataFrame()
    return df.astype({k: v for k, v in config.KOREA_SCHEMA.items() if k in df.columns})


def run() -> int:
    manual = _load_manual()
    frames = [f for f in (manual, _seed_frame()) if not f.empty]
    if not frames:
        storage.log_run("korea_customs", "empty")
        return 0
    data = pd.concat(frames, ignore_index=True)
    data = data.dropna(subset=["yoy_pct"])
    total = storage.write_table(data, "korea_exports", ["period", "window_type"])
    storage.log_run("korea_customs", "ok", rows=total,
                    detail="manual+seed; automate via data.go.kr key in v1")
    return total


if __name__ == "__main__":
    run()
