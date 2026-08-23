from __future__ import annotations

import argparse
import traceback
from datetime import datetime, timezone

import pandas as pd

from . import config, features, models, report, storage
from .ingest import korea_customs, markets, press, trendforce


def _recent_runs() -> list[dict]:
    path = config.LOGS_DIR / "runs.jsonl"
    if not path.exists():
        return []
    lines = path.read_text().strip().splitlines()
    today = datetime.now(timezone.utc).strftime(config.RUN_DATE_FMT)
    todays = [line for line in lines if f'"{today}' in line]
    keep, seen = [], set()
    for line in reversed(todays):
        import json

        d = json.loads(line)
        if d["source"] not in seen:
            seen.add(d["source"])
            keep.append(d)
    return list(reversed(keep))


def run(report_only: bool = False) -> None:
    if not report_only:
        for name, module in [
            ("markets", markets),
            ("trendforce", trendforce),
            ("korea_customs", korea_customs),
            ("press", press),
        ]:
            try:
                module.run()
            except Exception as exc:  # noqa: BLE001
                storage.log_run(name, "crashed", detail=f"{type(exc).__name__}: {exc}"[:200])
                traceback.print_exc()

    snap, alerts = features.current_snapshot()
    regime = features.classify_regime(snap)
    advice = features.consumer_advice(snap, regime[0])
    proxy = models.train_proxy_direction()
    preds = models.spot_predictions(snap)

    try:
        features.build_and_store(snap)
    except Exception as exc:  # noqa: BLE001
        storage.log_run("features_store", "error", detail=str(exc))

    try:
        models.append_run_to_ledger(snap, regime, advice, proxy, preds)
    except Exception as exc:  # noqa: BLE001
        storage.log_run("ledger", "error", detail=str(exc))

    leaderboard = None
    try:
        leaderboard = models.evaluate_ledger()
    except Exception as exc:  # noqa: BLE001
        storage.log_run("eval", "error", detail=str(exc))

    press_rows = storage.read_table("press_archive")
    content = report.render(
        snap=snap,
        alerts=alerts,
        regime=regime,
        advice=advice,
        proxy=proxy,
        preds=preds,
        source_status=_recent_runs(),
        press_rows=press_rows,
        leaderboard=leaderboard,
    )
    out = report.write_digest(content)
    print(f"digest written: {out}")
    try:
        from . import webgen

        page = webgen.build(state={"proxy": proxy, "preds": preds})
        print(f"dashboard written: {page}")
    except Exception as exc:  # noqa: BLE001
        storage.log_run("webgen", "error", detail=f"{type(exc).__name__}: {exc}"[:200])
        traceback.print_exc()
    print(f"regime={regime[0]} advice={advice[0]}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="oracle_pc")
    parser.add_argument("command", choices=["run", "report", "eval"])
    args = parser.parse_args()
    if args.command == "run":
        run()
    elif args.command == "report":
        run(report_only=True)
    elif args.command == "eval":
        board = models.evaluate_ledger()
        print(board.to_string(index=False) if not board.empty else "no scored predictions yet")


if __name__ == "__main__":
    main()
