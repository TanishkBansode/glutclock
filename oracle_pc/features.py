from __future__ import annotations

import numpy as np
import pandas as pd

from . import config, storage

_DDR5 = "DDR5 16Gb (2Gx8) 4800/5600"
_DDR5_ETT = "DDR5 16Gb (2Gx8) eTT"
_DDR4 = "DDR4 16Gb (2Gx8) 3200"
_NAND512 = "512Gb TLC"


def _pct_last(series: pd.Series, days: int) -> float | None:
    s = series.dropna()
    if len(s) < 2:
        return None
    cutoff = s.index[-1] - pd.Timedelta(days=days)
    older = s[s.index <= cutoff]
    if older.empty:
        return None
    base = float(older.iloc[-1])
    if base == 0:
        return None
    return (float(s.iloc[-1]) / base - 1.0) * 100.0


def _spot_item(prices: pd.DataFrame, item: str) -> pd.Series | None:
    sub = prices[prices["item"] == item]
    if sub.empty:
        return None
    s = sub.set_index(pd.to_datetime(sub["date"]))["session_avg"].sort_index()
    return s if len(s) else None


def equity_feature_frame(market: pd.DataFrame) -> pd.DataFrame:
    closes = market.pivot_table(index="date", columns="symbol", values="close", aggfunc="last")
    closes.index = pd.to_datetime(closes.index)
    closes = closes.sort_index().ffill()
    rets = closes.pct_change()

    basket = [t for t in config.MEMORY_BASKET if t in rets.columns]
    mem_ret = rets[basket].mean(axis=1)
    basket_index = (1.0 + mem_ret.fillna(0.0)).cumprod()
    start = mem_ret.first_valid_index()
    if start is not None:
        basket_index.loc[basket_index.index < start] = np.nan

    feats = pd.DataFrame(index=closes.index)
    feats["mem_mom_20d"] = basket_index.pct_change(20)
    feats["mem_mom_60d"] = basket_index.pct_change(60)
    roll_max = basket_index.rolling(250, min_periods=60).max()
    feats["mem_drawdown"] = basket_index / roll_max - 1.0
    if "^SOX" in rets.columns:
        feats["rs_mem_sox_60d"] = (
            mem_ret.rolling(60, min_periods=40).sum()
            - rets["^SOX"].rolling(60, min_periods=40).sum()
        )
        feats["sox_mom_20d"] = closes["^SOX"].pct_change(20)
    if "^TNX" in closes.columns:
        raw = closes["^TNX"].dropna()
        scale = 10.0 if float(raw.median()) > 20 else 1.0
        feats["rate_10y"] = closes["^TNX"] / scale
        feats["rate_chg_60d"] = feats["rate_10y"].diff(60)
    korea = [t for t in config.KOREA_MEMORY if t in rets.columns]
    if korea and "^KS11" in rets.columns:
        feats["krx_excess_60d"] = (
            rets[korea].mean(axis=1).rolling(60, min_periods=40).sum()
            - rets["^KS11"].rolling(60, min_periods=40).sum()
        )
    return feats


def _korea_features(korea: pd.DataFrame | None) -> dict:
    out = {"kr_d10_yoy": None, "kr_d10_accel": None}
    if korea is None or korea.empty:
        return out
    d10 = korea[korea["window_type"] == "D10"].copy()
    if d10.empty:
        return out
    d10 = d10.sort_values("period")
    out["kr_d10_yoy"] = float(d10["yoy_pct"].iloc[-1])
    if len(d10) >= 2:
        out["kr_d10_accel"] = out["kr_d10_yoy"] - float(d10["yoy_pct"].iloc[-2])
    return out


def current_snapshot() -> tuple[dict, dict]:
    prices = storage.read_table("physical_prices")
    market = storage.read_table("market_prices")
    korea = storage.read_table("korea_exports")

    snap: dict = {}
    alerts: list[str] = []

    if prices is not None and not prices.empty:
        bad = prices[~prices.get("sanity_ok", True).astype(bool)]
        for _, row in bad.iterrows():
            alerts.append(f"SANITY: {row['item']} jumped to {row['session_avg']} (quarantined)")
        clean = prices[prices.get("sanity_ok", True).astype(bool)]

        ddr5 = _spot_item(clean, _DDR5)
        if ddr5 is not None:
            snap["ddr5_spot"] = round(float(ddr5.iloc[-1]), 3)
            chg = _pct_last(ddr5, 7)
            snap["ddr5_chg_7d"] = None if chg is None else round(chg, 2)
        ett = _spot_item(clean, _DDR5_ETT)
        ddr5v = _spot_item(clean, _DDR5)
        if ett is not None and ddr5v is not None and float(ddr5v.iloc[-1]) > 0:
            snap["ett_discount"] = round(
                (1.0 - float(ett.iloc[-1]) / float(ddr5v.iloc[-1])) * 100.0, 1
            )
        ddr4 = _spot_item(clean, _DDR4)
        if ddr4 is not None and ddr5v is not None and float(ddr5v.iloc[-1]) > 0:
            snap["ddr4_ddr5_ratio"] = round(float(ddr4.iloc[-1]) / float(ddr5v.iloc[-1]), 2)
        nand = _spot_item(clean, _NAND512)
        if nand is not None:
            snap["nand512_spot"] = round(float(nand.iloc[-1]), 3)
            chg = _pct_last(nand, 7)
            snap["nand512_chg_7d"] = None if chg is None else round(chg, 2)

        today_mask = clean["date"] == clean["date"].max()
        todays = clean[today_mask]["session_change_pct"].dropna()
        if len(todays):
            snap["spot_breadth"] = round(float((todays > 0).mean()) * 100.0, 0)

    eq_feats = pd.DataFrame()
    if market is not None and not market.empty:
        eq_feats = equity_feature_frame(market)
        if not eq_feats.empty:
            last = eq_feats.dropna(how="all").iloc[-1]
            for col in ["mem_mom_20d", "mem_mom_60d", "mem_drawdown",
                        "rs_mem_sox_60d", "sox_mom_20d", "rate_10y", "krx_excess_60d"]:
                if col in last.index and pd.notna(last[col]):
                    snap[col] = round(float(last[col]), 4)

    snap.update(_korea_features(korea))

    if snap.get("kr_d10_accel") is not None and snap["kr_d10_accel"] < -10:
        alerts.append(f"Korea D10 semi-export YoY decelerating fast ({snap['kr_d10_accel']:+.1f} pts)")
    if snap.get("nand512_chg_7d") is not None and snap["nand512_chg_7d"] <= 0:
        alerts.append("NAND 512Gb spot flat/down over 7d window")
    if snap.get("spot_breadth") is not None and snap["spot_breadth"] < 40:
        alerts.append(f"Weak spot breadth: only {snap['spot_breadth']:.0f}% of items up on session")
    return snap, alerts


def classify_regime(snap: dict) -> tuple[str, str]:
    dd = snap.get("mem_drawdown")
    m20 = snap.get("mem_mom_20d")
    m60 = snap.get("mem_mom_60d")
    if dd is None or m20 is None or m60 is None:
        return "unknown", "insufficient market history"
    if dd <= -0.30 and m20 > 0:
        return "trough_recovery", f"drawdown {dd:.0%} with 20d momentum turning positive"
    if dd <= -0.25:
        return "contraction", f"memory equities in deep drawdown ({dd:.0%})"
    if m60 > 0 and dd > -0.10 and (m20 is not None and abs(m20) < abs(m60) * 0.5):
        return "maturing", "uptrend intact but 20d momentum well below 60d (deceleration)"
    if m60 > 0 and dd > -0.10:
        return "expansion", "momentum and drawdown both healthy"
    if m60 <= 0 and dd > -0.15:
        return "peak_risk", "momentum rolled over while prices remain near highs"
    return "contraction_watch", f"drawdown {dd:.0%}, 60d momentum {m60:+.1%}"


def consumer_advice(snap: dict, regime: str) -> tuple[str, str]:
    reasons = []
    wait_votes = 0
    if regime in ("expansion", "maturing", "peak_risk"):
        wait_votes += 1
        reasons.append(f"cycle regime={regime}: component prices still elevated/rising")
    acc = snap.get("kr_d10_accel")
    if acc is not None and acc < 0:
        wait_votes += 1
        reasons.append(f"Korea export YoY decelerating ({acc:+.1f} pts): supply catching up within quarters")
    nand7 = snap.get("nand512_chg_7d")
    if nand7 is not None and nand7 <= 0:
        wait_votes += 1
        reasons.append("NAND spot stalling: typical pre-price-relief signal")
    if regime == "trough_recovery":
        return "BUY", "equities signal trough; physical prices typically bottom 1-2 quarters later"
    if regime == "unknown":
        return "NEUTRAL", "not enough collected history yet"
    if wait_votes >= 2:
        return "WAIT", "; ".join(reasons)
    return "NEUTRAL", "; ".join(reasons) if reasons else "mixed signals"


def momentum_probability(chg_7d: float | None, chg_prev: float | None = None) -> float | None:
    if chg_7d is None:
        return None
    z = np.tanh(chg_7d / 5.0)
    return round(float(np.clip(0.5 + 0.35 * z, 0.05, 0.95)), 3)


def build_and_store(snap: dict) -> None:
    df = pd.DataFrame([{"date": pd.Timestamp.utcnow().strftime(config.RUN_DATE_FMT),
                        **{k: v for k, v in sorted(snap.items())}}])
    storage.write_table(df, "features_daily", ["date"])
