# SPEC.md — Refined Prompt & System Specification
## "GlutClock": Daily Memory-Market Monitor & Cycle-Turn Predictor

This is the refined, maximally technical version of your original request. Use it as the build contract. Everything below is implementable with free data sources.

---

## 1. One-sentence refined prompt (the original, sharpened)

> Build a self-updating Python system that, every day, ingests DRAM/NAND spot prices (TrendForce free pages + DXI), memory-sector equities and benchmarks (yfinance/Stooq), Korea Customs first-10-day semiconductor export prints, TrendForce press-release price forecasts, distributor/street component prices, Google Trends, and an RSS news stream classified by an LLM event extractor; maintains a Parquet time-series lake; computes leading-indicator features (spot–contract divergence, eTT/DDR4–DDR5 spread compression, Korean export second derivative, EPS-revision breadth, equity relative strength vs SOX, capex-event heat); runs a regime model (HMM + Bayesian online changepoint) plus calibrated LightGBM classifiers to output, daily: (a) current cycle-regime posterior {shortage, maturing, peak, contraction, trough}, (b) P(DDR5/NAND contract price up) for the next 1–3 months, (c) inflection alerts with lead-time/false-alarm tracking, (d) a consumer buy/wait recommendation for RAM and SSD purchases — all validated by walk-forward backtests against persistence baselines and archived TrendForce forecasts, logged with Brier scores on an automated leaderboard.

## 2. Architecture

```
┌──────────────────────── INGESTION (cron: 07:00 KST, 17:05 ET) ───────────────────────┐
│ adapters/                                                                            │
│   trendforce_prices  → DRAM spot, NAND spot/wafer, DXI      (HTML scrape, daily)     │
│   markets            → MU SKHY 000660.KS 005930.KS SNDK WDC STX 285A.T NVDA AMD    │
│                        TSM AAPL DELL HPQ ASML AMAT LRCX KLAC ^KS11 SMH ^IXIC ^TNX    │
│                        (yfinance primary, Stooq CSV fallback, retry+checksum)        │
│   korea_customs      → first-10-day / monthly semi exports YoY (KCS/data.go.kr)      │
│   trendforce_press   → press-center RSS/pages → %QoQ forecast extraction (regex+LLM) │
│   street_prices      → PCPartPicker/Newegg canonical kit prices (32GB DDR5, 2TB NVMe)│
│   google_trends      → pytrends "RAM price","SSD price" (weekly)                     │
│   news               → RSS list → LLM classifier → typed events JSON                 │
└──────────────┬───────────────────────────────────────────────────────────────────────┘
               ▼
┌── STORAGE: data/lake (Parquet, append-only, one partition per source/day) ──────────┐
│   DuckDB views; schema registry; quarantine table for failed sanity checks          │
└──────────────┬──────────────────────────────────────────────────────────────────────┘
               ▼
┌── FEATURES (features/build.py) ──────────────────────────────────────────────────────┐
│ momentum/z-scores · spot-contract gap · spreads (eTT, DDR4-DDR5, wafer-module)       │
│ korea_2nd_deriv · revision_breadth · eq_rel_strength(MU-bundle/SOX,60d)              │
│ capex_heat(90d event sum) · pull_forward_index · trends_z · freight/tariff flags     │
└──────────────┬───────────────────────────────────────────────────────────────────────┘
               ▼
┌── MODELS (models/) ──────────────────────────────────────────────────────────────────┤
│ M1 regime: Gaussian HMM(k=3..5) on standardized core features → state posteriors    │
│ M2 changepoint: Bayesian online changepoint on DDR5/NAND spot log-returns            │
│ M3 direction: LightGBM (monotone constraints) → P(contract Δ>0, horizon 1/2/3mo),    │
│    isotonic-calibrated via purged K-fold                                             │
│ M4 events: rule+LLM alert layer (fab_incident ⇒ vol flag; capex_announce ⇒ glut clock)│
│ ENSEMBLE: regime-gated blend; conformal intervals on numeric forecasts               │
└──────────────┬───────────────────────────────────────────────────────────────────────┘
               ▼
┌── OUTPUT (report/) ──────────────────────────────────────────────────────────────────┤
│ daily_digest.md + Telegram/email · dashboard (Streamlit): price panels, feature      │
│ dashboard, regime strip, prediction ledger w/ Brier leaderboard                      │
│ predictions.jsonl: {date, target, horizon, p, features_hash, model_version}          │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## 3. Prediction contract (exact targets)

| ID | Target | Type | Horizon | Eval |
|---|---|---|---|---|
| T1 | DDR5 16Gb contract QoQ > 0 | prob | 1,2,3 mo | Brier + DM test vs persistence & vs archived TrendForce |
| T2 | NAND wafer contract QoQ > 0 | prob | 1,2,3 mo | same |
| T3 | Regime label | 5-class posterior | nowcast | accuracy + transition-recall@lead≥4wks |
| T4 | Spot turn flag (NAND/DDR5) | binary alarm | ≤8 wk lead | ROC-AUC, false alarms/yr |
| T5 | Consumer advice | buy/hold/wait | rolling | realized savings vs naive-dated purchase |

## 4. Non-negotiable engineering rules

1. **No lookahead**: every feature uses only data published ≤ t. TrendForce forecast rows stamped at *publication* date, never period-covered date. Purged+embargoed (40 trading days) walk-forward CV only.
2. **Baselines in the ledger forever**: persistence, seasonal-naive, "TrendForce said". A model that can't beat them is labeled as such in the UI.
3. **Idempotent, replayable ingestion**: any day's run reproducible from `git rev` + raw snapshots.
4. **Sanity gates**: d/d price moves >35% quarantined; currency/unit checks; source-shape contracts (selectors versioned).
5. **Calibration or nothing**: raw model scores are never shown; only calibrated probabilities with reliability plots.
6. **Structural-break flag**: pre-2024 samples down-weighted (LTA regime); UI shows which regime the model was trained on.

## 5. Roadmap

- **v0 (build now)**: ingestion for TrendForce prices + yfinance basket + Korea customs + press archive; storage; 10 core features; persistence baseline + simple logistic/HMM; markdown digest; prediction ledger.
- **v1**: LightGBM + calibration + walk-forward harness; changepoint alarms; Telegram bot; Streamlit dashboard.
- **v2**: LLM event extractor over news; capex/glut-clock tracker; street-price scrapers; Trends; conformal intervals; automated TrendForce beat-score.
- **v3**: multi-region street prices; smartphone side; HDD/nearline series; scenario simulator ("if AI capex −20% → supply/demand crossover moves to …").

## 6. Success criteria

- Ingestion uptime ≥99% over 90 days; zero silent failures (all failures alert).
- Direction models: Brier improvement ≥5% vs persistence out-of-sample, or honest red label.
- ≥1 documented instance of flagging a real deceleration signal earlier than mainstream sell-side commentary (e.g., Korea 10-day YoY rollover).
- Consumer layer: demonstrates positive expected savings vs random-date buying in backtest of 2020–2026 cycles.
