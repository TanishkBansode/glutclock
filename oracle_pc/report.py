from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config

FEATURE_LABELS = [
    ("ddr5_spot", "DDR5 16Gb spot (USD)"),
    ("ddr5_chg_7d", "DDR5 spot chg 7d (%)"),
    ("nand512_spot", "NAND 512Gb TLC spot (USD)"),
    ("nand512_chg_7d", "NAND 512Gb chg 7d (%)"),
    ("ett_discount", "DDR5 eTT discount (%)"),
    ("ddr4_ddr5_ratio", "DDR4/DDR5 price ratio"),
    ("spot_breadth", "Spot breadth (% items up)"),
    ("kr_d10_yoy", "Korea D10 semi exports YoY (%)"),
    ("kr_d10_accel", "Korea YoY acceleration (pts)"),
    ("mem_mom_20d", "Memory basket momentum 20d"),
    ("mem_mom_60d", "Memory basket momentum 60d"),
    ("mem_drawdown", "Memory basket drawdown from 250d high"),
    ("rs_mem_sox_60d", "Memory basket vs SOX 60d excess"),
    ("sox_mom_20d", "SOX momentum 20d"),
    ("rate_10y", "US 10Y yield (%)"),
]


def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:,.2f}"
    return str(v)


def render(snap: dict, alerts: list[str], regime: tuple[str, str],
           advice: tuple[str, str], proxy: dict, preds: list[dict],
           source_status: list[dict], press_rows: pd.DataFrame | None,
           leaderboard: pd.DataFrame | None) -> str:
    lines = []
    lines.append(f"# GlutClock Daily Digest — {pd.Timestamp.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    lines.append(f"## Verdict")
    lines.append(f"- **Cycle regime:** `{regime[0]}` — {regime[1]}")
    lines.append(f"- **Consumer advice:** **{advice[0]}** — {advice[1]}")
    if proxy.get("status") == "ok":
        lines.append(
            f"- **Proxy model** P(memory equities up next 5d): **{proxy['p_memory_basket_up_5d']:.0%}** "
            f"(test Brier {proxy.get('brier','-')} vs majority acc {proxy.get('majority_baseline_acc','-')}, asof {proxy.get('asof','?')})"
        )
    else:
        lines.append(f"- **Proxy model:** warming up ({proxy.get('status')}) — learned direction calls activate once enough history accrues.")
    lines.append("")

    lines.append("## Key indicators")
    lines.append("| Indicator | Value |")
    lines.append("|---|---|")
    for key, label in FEATURE_LABELS:
        if key in snap:
            lines.append(f"| {label} | {_fmt(snap[key])} |")
    lines.append("")

    if preds:
        lines.append("## Today's predictions (logged to ledger)")
        lines.append("| Target | Horizon | Model P(up) | Constant baseline | Note |")
        lines.append("|---|---|---|---|---|")
        for p in preds:
            pm = f"{p['p_model']:.2f}" if p["p_model"] is not None else "-"
            lines.append(f"| {p['target']} | {p['horizon_days']}d | {pm} | {p['p_constant']:.2f} | {p['note']} |")
        lines.append("")

    if alerts:
        lines.append("## Alerts")
        for a in alerts:
            lines.append(f"- ⚠️ {a}")
        lines.append("")

    if press_rows is not None and not press_rows.empty:
        mem = press_rows[press_rows.get("is_memory", True).astype(bool)] if "is_memory" in press_rows.columns else press_rows
        recent = mem.sort_values("published", ascending=False).head(5)
        lines.append("## Latest TrendForce memory press items (archived)")
        for _, row in recent.iterrows():
            forecasts = row["forecasts_json"]
            lines.append(f"- [{row['published']}] {row['title'][:120]}… {forecasts if forecasts != '[]' else ''}")
        lines.append("")

    lines.append("## Source status (this run)")
    lines.append("| Source | Status | Rows | Detail |")
    lines.append("|---|---|---|---|")
    for s in source_status:
        lines.append(f"| {s['source']} | {s['status']} | {s['rows']} | {s['detail'][:80]} |")
    lines.append("")

    if leaderboard is not None and not leaderboard.empty:
        lines.append("## Prediction scoreboard (vs baselines)")
        lines.append(leaderboard.to_markdown(index=False))
        lines.append("")

    lines.append("---")
    lines.append("*Baselines are permanent: a model that cannot beat them is labeled as such. Physical-price history starts at system deployment; equity features use deep history immediately.*")
    return "\n".join(lines)


def write_digest(content: str) -> Path:
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    out = config.LOGS_DIR / "digest.md"
    out.write_text(content)
    return out
