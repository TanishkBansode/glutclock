# GlutClock — daily memory-market monitor & cycle-turn predictor (v0)

Tracks DRAM/NAND spot prices, memory-sector equities, Korean export telemetry, and TrendForce
press forecasts every day; computes leading-indicator features; classifies the cycle regime;
logs calibrated predictions against permanent baselines; emits `logs/digest.md`.

Read `SPEC.md` for the full design contract and `RESEARCH.md` for the market research behind it.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m oracle_pc.pipeline run     # first run backfills ~2y of market data
```

## Daily operation

### Option A — GitHub Actions (recommended, free)

The repo ships `.github/workflows/daily.yml`: it runs the pipeline twice a day
(01:00 UTC pre-US / 21:15 UTC post-US-close weekdays), commits fresh `data/`, `logs/`, and `web/`
back to the repo, and publishes the dashboard to **GitHub Pages**.

```bash
git init && git add -A && git commit -m "GlutClock v0"
git remote add origin git@github.com:YOU/glutclock.git
git push -u origin main
```

Then in the repo settings enable **Settings → Pages → Source: GitHub Actions**.
The first scheduled run (or any manual "Run workflow" on the Actions tab) builds the site at:
`https://YOU.github.io/glutclock/`

Notes: state persists because every run commits the parquet lake back to git; yfinance is
occasionally rate-limited on CI runners — US names fall back to Stooq automatically, KRX/JPX rows
simply skip that day.

### Option B — local cron

```bash
./run_daily.sh                                 # what cron should call
crontab -e                                     # add:
0 9 * * * /home/tanx/project/futureofcomputer/run_daily.sh
```

Commands: `run` (ingest + features + models + ledger + digest + dashboard)
· `report` (digest/dashboard only, no network) · `eval` (score logged predictions whose horizon has elapsed).

## Outputs

| Path | Contents |
|---|---|
| `logs/digest.md` | daily verdict: regime, advice, indicators, alerts, predictions |
| `web/index.html` | self-contained dashboard (charts + ledger + scoreboard) — published to GitHub Pages |
| `data/lake/*.parquet` | append-only lake: `physical_prices`, `market_prices`, `korea_exports`, `press_archive`, `features_daily` |
| `data/predictions.jsonl` | prediction ledger (one JSON per run, with feature snapshot hash) |
| `logs/runs.jsonl` | per-source ingestion audit trail |

Query the lake with SQL:

```bash
.venv/bin/python -c "from oracle_pc.storage import sql; print(sql(\"select date,item,session_avg from 'data/lake/physical_prices.parquet' order by date desc limit 5\"))"
```

## Data sources & status

- **TrendForce free price pages** (scraped): DRAM spot, NAND flash spot, SSD street prices. Daily.
  Historical physical prices are paywalled — our own history starts at deployment date, which is
  exactly why archiving starts now.
- **Equities**: yfinance primary, Stooq fallback. Basket covers memory makers, demand drivers,
  equipment enablers, benchmarks (see `oracle_pc/config.py`).
- **Korea Customs first-10-day semiconductor exports**: currently seeded with known prints
  (Jun/Jul/Aug 2026). Drop new rows into `data/manual/korea_semi_exports.csv`
  (`period,window_type,exports_usd_mn,yoy_pct`) each month; automation via data.go.kr API key is v1.
- **TrendForce press center**: archived daily; %QoQ forecast ranges extracted by regex to build a
  scoreable record of their forecasts.

## Honest state of v0

- Physical-price models are cold-starting: direction probabilities activate after ~60 days of
  collected prices. The equity-based proxy model trains immediately but is only marginally better
  than chance out-of-sample — it is displayed with its Brier score so this is never hidden.
- Regime labels are equity-implied and rule-based; HMM + LightGBM layers land in v1/v2 per SPEC.md.
- A model that cannot beat the constant-0.5 baseline is labeled as such in every digest.

## Roadmap

v1: calibration + walk-forward harness · changepoint alarms · Telegram digest.
v2: LLM event extractor · capex/glut clock · street-price scrapers · conformal intervals.
v3: scenario simulator · HDD/nearline series · smartphone side.
