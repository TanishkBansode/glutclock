from __future__ import annotations

import numpy as np
import pandas as pd

from . import config, storage
from .features import equity_feature_frame

HORIZON_DAYS = 5


def make_supervised(feats: pd.DataFrame, closes: pd.Series) -> pd.DataFrame:
    df = feats.copy()
    df["target_up"] = (closes.shift(-HORIZON_DAYS) / closes - 1.0 > 0).astype(float)
    df = df.dropna(subset=[c for c in df.columns if c != "target_up"])
    df = df.dropna(subset=["target_up"])
    return df


def train_proxy_direction() -> dict:
    market = storage.read_table("market_prices")
    if market is None or market.empty:
        return {"status": "no_data"}
    closes = market.pivot_table(index="date", columns="symbol", values="close", aggfunc="last")
    closes.index = pd.to_datetime(closes.index)
    basket = [t for t in config.MEMORY_BASKET if t in closes.columns]
    mem = closes[basket].mean(axis=1).sort_index()
    feats = equity_feature_frame(market).dropna(how="all")
    data = make_supervised(feats, mem)
    if len(data) < 120:
        return {"status": "insufficient_history", "rows": len(data)}

    split = int(len(data) * 0.8)
    X_cols = [c for c in data.columns if c != "target_up"]
    X_train, y_train = data[X_cols].iloc[:split], data["target_up"].iloc[:split]
    X_test, y_test = data[X_cols].iloc[split:], data["target_up"].iloc[split:]

    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    model = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=1000))
    model.fit(X_train, y_train)

    result = {"status": "ok", "train_rows": int(split), "test_rows": int(len(y_test))}
    if len(y_test) > 20:
        proba = model.predict_proba(X_test)[:, 1]
        brier = float(np.mean((proba - y_test.to_numpy()) ** 2))
        acc = float(((proba > 0.5).astype(float) == y_test.to_numpy()).mean())
        base = float(max(y_test.mean(), 1 - y_test.mean()))
        result.update({"brier": round(brier, 4),
                       "accuracy": round(acc, 3),
                       "majority_baseline_acc": round(base, 3)})
    latest = data[X_cols].iloc[[-1]]
    p_up = float(model.predict_proba(latest)[0, 1])
    result["p_memory_basket_up_5d"] = round(p_up, 3)
    result["asof"] = str(data.index[-1].date())
    return result


def spot_predictions(snap: dict) -> list[dict]:
    preds = []
    for target_id, series_key in [
        ("T1_ddr5_spot_dir_7d", "ddr5_chg_7d"),
        ("T2_nand512_spot_dir_7d", "nand512_chg_7d"),
    ]:
        chg = snap.get(series_key)
        p_mom = None
        if chg is not None:
            import numpy as _np

            z = float(_np.tanh(chg / 5.0))
            p_mom = round(float(np.clip(0.5 + 0.35 * z, 0.05, 0.95)), 3)
        preds.append(
            {
                "target": target_id,
                "horizon_days": 7,
                "p_model": p_mom,
                "p_constant": 0.5,
                "note": "momentum heuristic; learned model pending 60+ days of physical prices",
            }
        )
    return preds


def append_run_to_ledger(snap: dict, regime: tuple[str, str], advice: tuple[str, str],
                         proxy: dict, preds: list[dict]) -> None:
    from .storage import append_ledger, features_hash

    record = {
        "ts": pd.Timestamp.utcnow().isoformat(timespec="seconds"),
        "run_date": pd.Timestamp.utcnow().strftime(config.RUN_DATE_FMT),
        "model_version": config.MODEL_VERSION,
        "features_hash": features_hash({k: v for k, v in snap.items()}),
        "regime": regime[0],
        "advice": advice[0],
        "proxy_direction_model": {k: v for k, v in proxy.items() if k != "status"},
        "predictions": preds,
        "features_snapshot": snap,
    }
    append_ledger(record)


def evaluate_ledger() -> pd.DataFrame:
    import json

    if not config.LEDGER_PATH.exists():
        return pd.DataFrame()
    records = [json.loads(line) for line in open(config.LEDGER_PATH)]
    if not records:
        return pd.DataFrame()
    rows = []
    for rec in records:
        for pred in rec.get("predictions", []):
            due = pd.Timestamp(rec["run_date"]) + pd.Timedelta(days=pred["horizon_days"])
            rows.append({
                "run_date": rec["run_date"],
                "target": pred["target"],
                "p_model": pred["p_model"],
                "p_constant": pred["p_constant"],
                "outcome_due": str(due.date()),
                "model_version": rec.get("model_version"),
            })
    ledger_df = pd.DataFrame(rows)
    prices = storage.read_table("physical_prices")
    if prices is None or prices.empty:
        return pd.DataFrame()
    outcomes = []
    for _, row in ledger_df.iterrows():
        item_map = {
            "T1_ddr5_spot_dir_7d": "DDR5 16Gb (2Gx8) 4800/5600",
            "T2_nand512_spot_dir_7d": "512Gb TLC",
        }
        item = item_map.get(row["target"])
        sub = prices[(prices["item"] == item) & (prices["sanity_ok"])]
        sub = sub.sort_values("date").set_index("date")["session_avg"]
        due = row["outcome_due"]
        base_dates = [d for d in sub.index if d <= str(pd.Timestamp(row["run_date"]).date())]
        future_dates = [d for d in sub.index if d >= due]
        if not base_dates or not future_dates:
            continue
        start_v, end_v = float(sub.loc[base_dates[-1]]), float(sub.loc[future_dates[0]])
        if start_v == 0:
            continue
        outcomes.append(1.0 if end_v / start_v - 1 > 0 else 0.0)
    ledger_df["outcome"] = pd.Series(outcomes)
    scored = ledger_df.dropna(subset=["outcome"])
    if scored.empty:
        return pd.DataFrame()
    summary = []
    for target, grp in scored.groupby("target"):
        for model_col in ["p_model", "p_constant"]:
            valid = grp.dropna(subset=[model_col])
            if valid.empty:
                continue
            summary.append({
                "target": target,
                "model": model_col,
                "n": len(valid),
                "brier": round(float(((valid[model_col] - valid["outcome"]) ** 2).mean()), 4),
                "accuracy": round(float(((valid[model_col] > 0.5).astype(float) == valid["outcome"]).mean()), 3),
            })
    return pd.DataFrame(summary)
