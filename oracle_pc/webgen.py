from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from . import config, features, models, storage

_WEB_DIR = config.BASE_DIR / "web"
_TEMPLATE = Path(__file__).parent / "templates" / "dashboard.html"
_PLACEHOLDER = "__GLUTCLOCK_PAYLOAD__"
_STATIC_PAGES = ["about.html", "guide.html", "method.html"]


def _basket_and_sox(market: pd.DataFrame) -> dict:
    closes = market.pivot_table(index="date", columns="symbol", values="close", aggfunc="last")
    closes.index = pd.to_datetime(closes.index)
    closes = closes.sort_index().ffill()
    rets = closes.pct_change()
    basket = [t for t in config.MEMORY_BASKET if t in rets.columns]
    mem_ret = rets[basket].mean(axis=1)
    idx = (1.0 + mem_ret.fillna(0.0)).cumprod()
    start = mem_ret.first_valid_index()
    if start is not None:
        idx.loc[idx.index < start] = pd.NA
    idx = idx.dropna()
    out = {
        "dates": idx.index.strftime("%Y-%m-%d").tolist(),
        "memory": [round(float(v), 2) for v in (idx / idx.iloc[0] * 100.0)],
        "sox": [],
    }
    if "^SOX" in closes.columns:
        sox = closes["^SOX"].reindex(idx.index).ffill().bfill()
        out["sox"] = [round(float(v), 2) for v in (sox / sox.iloc[0] * 100.0)]
    return out


def _spot_series(prices: pd.DataFrame, item: str) -> dict:
    sub = prices[prices["item"] == item].sort_values("date")
    return {
        "dates": sub["date"].tolist(),
        "values": [round(float(v), 3) for v in sub["session_avg"]],
    }


def _korea_series(korea: pd.DataFrame) -> dict:
    d10 = korea[korea["window_type"] == "D10"].sort_values("period")
    yoy = [float(v) for v in d10["yoy_pct"]]
    accel = [None] + [round(yoy[i] - yoy[i - 1], 1) for i in range(1, len(yoy))]
    return {"labels": d10["period"].tolist(), "yoy": yoy, "accel": accel}


def _ledger_rows(limit: int = 30) -> list[dict]:
    if not config.LEDGER_PATH.exists():
        return []
    rows = []
    for line in open(config.LEDGER_PATH):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        for pred in rec.get("predictions", []):
            rows.append(
                {
                    "date": rec.get("run_date"),
                    "target": pred.get("target"),
                    "p_model": pred.get("p_model"),
                    "p_const": pred.get("p_constant"),
                    "regime": rec.get("regime"),
                    "advice": rec.get("advice"),
                }
            )
    return rows[-limit:]


def build(state: dict | None = None) -> Path:
    prices = storage.read_table("physical_prices")
    market = storage.read_table("market_prices")
    korea = storage.read_table("korea_exports")

    snap, alerts = features.current_snapshot()
    regime = features.classify_regime(snap)
    advice = features.consumer_advice(snap, regime[0])
    proxy = (state or {}).get("proxy") or models.train_proxy_direction()
    preds = (state or {}).get("preds") or models.spot_predictions(snap)

    spots = {}
    if prices is not None and not prices.empty:
        spots["ddr5"] = _spot_series(prices, "DDR5 16Gb (2Gx8) 4800/5600")
        spots["nand512"] = _spot_series(prices, "512Gb TLC")
    equity = _basket_and_sox(market) if market is not None and not market.empty else {}
    korea_data = _korea_series(korea) if korea is not None and not korea.empty else {}

    scoreboard: list[dict] = []
    try:
        board = models.evaluate_ledger()
        if not board.empty:
            scoreboard = board.to_dict(orient="records")
    except Exception:
        pass

    payload = {
        "generated": pd.Timestamp.utcnow().isoformat(timespec="seconds"),
        "modelVersion": config.MODEL_VERSION,
        "snap": snap,
        "alerts": alerts,
        "regime": {"label": regime[0], "reason": regime[1]},
        "advice": {"label": advice[0], "reason": advice[1]},
        "proxy": proxy,
        "preds": preds,
        "spots": spots,
        "equity": equity,
        "korea": korea_data,
        "ledger": _ledger_rows(),
        "scoreboard": scoreboard,
    }

    html = _TEMPLATE.read_text().replace(_PLACEHOLDER, json.dumps(payload, default=str).replace("</", "<\\/"))
    _WEB_DIR.mkdir(parents=True, exist_ok=True)
    for page in _STATIC_PAGES:
        shutil.copyfile(_TEMPLATE.parent / page, _WEB_DIR / page)
    out = _WEB_DIR / "index.html"
    out.write_text(html)
    return out
