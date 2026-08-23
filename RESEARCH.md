# The Personal Computer Component Market: Full Technical Research Dossier
*Compiled August 23, 2026. Sources: TrendForce/DRAMeXchange, IDC, Gartner, Counterpoint, company filings, CNBC, Bloomberg/Yahoo, Korea Customs Service.*

---

## 1. Market Structure (who actually sets your RAM/SSD price)

### 1.1 DRAM oligopoly (~95%+ of global supply)
| Producer | Ticker(s) | Notes |
|---|---|---|
| Samsung Electronics | 005930.KS (KRX) | Reclaimed #1 DRAM share Q2 2026 (Counterpoint). ~60–70% of capacity moving to long-term agreements (LTAs). 2026 investment >₩110T. |
| SK hynix | **SKHY** (Nasdaq, listed July 2026, raised $26.5B), 000660.KS | #1 in HBM (58% share Q1 2026, Counterpoint). Record 76% op margin. ₩40T buyback Aug 2026. $720B Yongin cluster master plan. |
| Micron | MU (Nasdaq) | Only US-based maker. FQ3'26 (ended May 28): rev $41.5B, GM 84.9%, guided ~86%. FY27 capex > mid-$40Bs. $250B US investment through 2035. |
| CXMT (ChangXin) | unlisted | Chinese challenger; ramping DDR4/DDR5; geopolitical wildcard that caps the cycle's ceiling. |

### 1.2 NAND flash
Samsung, Kioxia (285A.T), SanDisk (SNDK, spun from Western Digital Feb 2025), SK hynix/Solidigm, Micron, YMTC (China). Same oligopoly dynamics; NAND historically more brutal cycles than DRAM because bit growth per wafer is easier.

### 1.3 Adjacent chokepoints
- **TSMC (TSM)**: CoWoS advanced packaging gates all HBM→GPU flow. 20–30 week lead times at peaks. Q2'26 rev $40.2B @ 60.3% OM.
- **ASML, AMAT, LRCX, KLAC, Tokyo Electron**: equipment book-to-bill is a *leading* indicator of future supply (fab tool-ins precede bits by 12–24 months).
- **Seagate (STX), WDC**: nearline HDD shortage is pushing hyperscalers to high-capacity QLC SSDs — a structural NAND demand amplifier.
- **PC OEMs**: Dell (DELL), HP (HPQ), Lenovo (0992.HK), Apple (AAPL) — their config cuts (RAM/SSD derating) are a real-time demand-destruction signal.
- **GPU**: NVIDIA (NVDA) is effectively the demand dictator — its platform ramps (Blackwell → Vera Rubin) pull DRAM/HBM/enterprise-SSD demand forward.

### 1.4 How prices actually form (mechanics)
- **Spot market** (daily, brokers/module houses, Taiwan): high-frequency, volatile, *leads* contract by 1–3 months at turning points. Tracked by DRAMeXchange/TrendForce (free daily quotes at trendforce.com/price/), also the **DXI index** (DRAMeXchange Index, daily).
- **Contract market** (monthly for DRAM/NAND chips, quarterly for SSDs): negotiated between makers and OEMs/CSPs. This is what actually drives BOM costs. Historically confidential; TrendForce publishes ranges + %QoQ forecasts in free press releases.
- **eTT** (Taiwan-marketed, lower-grade chips): the discount series; widening/narrowing eTT spread = quality of demand signal.
- **LTAs / take-or-pay**: NEW structural feature since 2025–26. Micron: 16 strategic agreements, ~$100B minimum cumulative revenue, ~$22B deposits. SanDisk: $93.9B minimum revenue w/ 8 customers. This flattens future troughs AND delays peak signals — the old cycle timing models understate how much contract prices are now decoupled from spot.
- **HBM trade ratio**: each HBM generation consumes ~3x the wafer per usable bit vs standard DDR5 (Micron disclosure). HBM growth mechanically *shrinks* conventional DRAM supply. This is THE core mechanism of the 2025–26 crisis.

### 1.5 Anatomy of a memory cycle (100-year pattern)
```
Shortage -> panic buying + double-ordering -> inventory overstatement
        -> PEAK (spot stalls while contract lags upward; second-derivative flips negative)
        -> demand destruction (OEMs cut configs, consumers delay)
        -> new fabs tool-in (18-30 mo lag after capex announcement) -> GLUT (prices -50~-80%)
        -> capex cuts, production curtailments, losses -> trough -> recovery
```
Historical anchors: 1996, 2001, 2008, 2011 (Thai floods — HDD), 2013 (SK hynix Wuxi fire — spot +50% in weeks), 2017–18 boom → 2019 DRAM −60%, 2020–21 COVID boom → 2022–23 NAND bust (−80%+, forced production cuts), 2023 recovery → **2025–26 AI supercycle (current)**.

---

## 2. Current Scenario Snapshot (August 23, 2026)

### 2.1 Physical market — late-stage upturn, second derivative already negative
| Series | Latest | Trajectory |
|---|---|---|
| Conventional DRAM contract QoQ | +58–63% (2Q26 actual) | Forecast **+13–18%** 3Q26 (TrendForce) → sharp deceleration |
| NAND flash contract QoQ | +70–75% (2Q26) | Forecast **+10–15%** 3Q26 |
| Enterprise SSD contract QoQ | >50% (1Q26), 48–53% (2Q26) | Moderated to **+20–25%** 3Q26 |
| DDR5 16Gb spot (session avg) | ~$54 | Still grinding up but narrow breadth |
| DDR4 16Gb spot | ~$91 (!!) | Legacy EOL squeeze; extreme scarcity premium |
| **NAND wafer spot** | **Stopped rising in July 2026**, range-bound, thin volumes | ⚠️ Classic pre-top signal |
| Spot vs contract behavior | Spot consolidating while contract still rises | ⚠️ Contract lag phase = cycle maturity |

### 2.2 Demand side — destruction underway in client, roaring in AI
- IDC: 2026 PC shipments **−11.3%** (Q4'26 YoY as bad as **−20%**); PC ASP **+17–18.3%**; relief not before end-2027; stabilization 2028.
- Gartner: combined DRAM+SSD prices **+130%** by end-2026; memory hits **23% of PC BOM** (vs 16% in 2025); **sub-$500 laptops extinct by 2028**; PC lifetime extended 15–20%; AI PC 50% penetration pushed to 2028.
- OEM response: shipping devices with derated RAM/SSD configs (12GB→8GB, 256GB→128GB phones; same in PCs).
- Q4'25–Q1'26 **pull-forward**: buyers front-loaded purchases ahead of hikes → payback quarter(s) ahead.
- AI/server side: HBM sold out through 2026 across all three makers; CSPs signing multi-year LTAs; enterprise SSD shortage expected until late-2027/2028 capacity arrives.

### 2.3 Supply side — the seeds of the NEXT glut are being planted NOW
- Combined industry capex ~₩200T (~$129B+) in 2026 alone; every major is expanding simultaneously (they always overshoot collectively):
  - SK hynix: M15X Cheongju producing since Feb 2026; Yongin Fab 1 cleanroom pulled forward to **Feb 2027**; Y2 fab announced Aug 7 2026 (₩54T); M17 NAND fab; Indiana packaging 2028; Nasdaq proceeds $26.5B.
  - Samsung: P5 Pyeongtaek online 2028; first Yongin fab pulled toward H2 2029; Gwangju cluster ₩400T plan; ending MLC NAND June 2026 (−40% global MLC capacity).
  - Micron: ID1 Idaho first wafers ~mid-2027; NY megafab ($100B campus); Singapore packaging 2027; Tongluo Taiwan expansion.
  - Meaningful new conventional bits: **H2 2027 → 2028**. Consensus (Counterpoint): prices unlikely to soften before end-2028 *if AI demand keeps growing*. That "if" is the whole ballgame.
- Reuters Jan 2026: new conventional memory fabs not online until 2027–28; every 2027–28 delivery commitment is being written against capacity that doesn't exist yet.

### 2.4 Financial market — ALREADY pricing the turn (critical!)
From close before Micron earnings (Jun 24) to Aug 6, despite RECORD results/guidance: **MU −14.8%, STX −15.7%, WDC −19.4%, SNDK −29.5%, Samsung −32.2%, SKHY −42.8%, Kioxia −46.9%**. Bloomberg (Aug 21): "smart money is moving on"; stocks stuck at May levels; concerns = rising rates, circular AI financing, crowding (SNDK most over-owned S&P name in Q2 per Morgan Stanley). Micron FY27 EPS estimate revisions have *stalled* (+1.2% last month vs huge prior revisions) — revision momentum dying is a top-tier sell-signal in cyclicals. Equities bottom-tick cycles ~2–3 quarters before spot/contract prices do. **The equity tape is currently voting: up-cycle matures within ~2–4 quarters.**

### 2.5 Macro/trade telemetry (highest-frequency hard data available)
- Korea Customs **first-10-day** semi exports: Aug 1–20 +198.8% YoY, semis = record 47.2% of ALL Korean exports; monthly semi exports >$40B every month since June 2026. Watch the *deceleration* of this YoY number, not its level.
- China semi exports H1'26 +95.6% YoY (CXMT et al scaling).
- Rates rising; AI-capex financing migrating to credit markets → macro fragility lever on the whole complex.
- Wildcards: TurboQuant-type algorithmic efficiency shocks (caused sharp memory-stock selloff on release), Middle East shipping/freight, tariffs, China-Taiwan risk, fab incidents (fire/power/quake) which can spike spot ±20% in days.

### 2.6 Synthesis
We sit in the **late-upcycle regime**: fundamentals still rising, pace decelerating, spot plateauing, equities rolled over, capex surging, consumer demand destroyed. Base case: contract prices keep rising into 1H27 (LTAs enforce floors), then flatten; genuine glut risk concentrated 2028+ when Yongin/P5/Idaho/New York/CXMT bits land — earlier if AI capex cracks, later if Vera Rubin/Rubin-class demand outruns supply. For a PC buyer: **prices stay ugly through 2027; the buying window is likely late-2028+** (subject to what the monitoring program says in real time).

---

## 3. Indicator Taxonomy (what the daily program must watch, by horizon)

### Tier A — daily, machine-readable today
1. **TrendForce free price pages** (scrape): DRAM spot (DDR5 16Gb, DDR4 16Gb/8Gb, eTT variants), NAND spot/wafer, session avg + Δ%. Also DXI current value.
2. **Equities**: MU, SKHY, 000660.KS, 005930.KS, SNDK, WDC, STX, Kioxia(285A.T), NVDA, AMD, INTC, TSM, DELL, HPQ, AAPL, ASML, AMAT, LRCX, KLAC, ^KS11, ^SOX/SMH, ^IXIC, 10Y yield (TNX). Via yfinance/Stooq fallbacks.
3. **News/event stream**: RSS (Reuters/Bloomberg/Tom's Hardware/TrendForce press center/Company IR) → LLM event extractor tagging {capex_announce, fab_incident, guidance_change, lta_signing, price_forecast_revision, technology_shock, geopolitics}.

### Tier B — weekly
4. Module/broker quotes, eTT discount width, DDR4−DDR5 spread, NAND wafer−DIMM spread (spread compression = demand-quality deterioration).
5. Distributor telemetry: Digi-Key/Mouser stock status & lead times for DRAM modules/NAND; PCPartPicker/Newegg street-price scrapes of canonical kits (e.g., 32GB DDR5-6000, 2TB PCIe4 SSD) — the *actual consumer experience* of price.
6. Google Trends: "RAM price", "SSD price", "DDR5", regional splits — retail panic gauge.

### Tier C — monthly (the heavyweight leading indicators)
7. **Korea Customs first-10-day & full-month semiconductor exports** (YoY, and crucially the *acceleration*, i.e., ΔYoY). Published ~mid-month; free via Korea Customs/data.go.kr/KITA. Best public real-time proxy for memory ASP×volume.
8. TrendForce monthly bulletins & quarterly price-forecast press releases (%QoQ ranges — archive every one, they're the closest thing to a consensus benchmark you can score yourself against).
9. China imports of semiconductors (volume vs value divergence = price vs quantity story).
10. SEMI equipment billings, ASML bookings (capex pipeline temperature).

### Tier D — quarterly (grading events)
11. Earnings: MU (late Mar/Jun/Sep/Dec), SKHY, Samsung, Kioxia, SNDK/WDC/STX. Extract: ASP QoQ, bit shipment QoQ, GM, capex guide, inventory days, LTA coverage commentary. **Guidance-revision momentum** (consensus FY EPS drift) is a first-class feature.
12. IDC/Gartner PC & smartphone trackers (units, ASPs, inventory commentary).
13. Steam Hardware Survey (client GPU mix → DIY demand pulse).

### Derived alpha features (engineering targets)
- `spot_contract_gap`: z-score of (spot MoM − contract QoQ annualized) — divergence = turn approaching.
- `korea_export_2nd_deriv`: ΔΔYoY of 10-day exports — historically rolls over 1–2 quarters before contract prices peak.
- `revision_breadth`: fraction of memory-name consensus EPS estimates revised down over trailing 4wks.
- `equity_relative_strength`: MU/SKH basket vs SOX, 60d — memory-specific derating.
- `capex_heat`: normalized sum of announced capex events trailing 90d — predicts supply 12–24mo out (glut clock).
- `spread_composite`: PCA factor of {eTT discount, DDR4-DDR5, wafer-module, HDD-QLC-per-TB}.
- `pull_forward_index`: PC shipment surprise vs trend + channel inventory commentary sentiment.

---

## 4. Companies & Stock Map (monitoring universe)

| Bucket | Names |
|---|---|
| Memory pure-plays | MU, SKHY, 000660.KS, SNDK, 285A.T (Kioxia) |
| Conglomerates | 005930.KS (Samsung), WDC, STX |
| Demand drivers | NVDA, AMD, AVGO, TSM, AAPL, DELL, HPQ, 0992.HK (Lenovo), MSFT/AMZN/GOOGL/META (CSP capex) |
| Supply enablers (glut clock) | ASML, AMAT, LRCX, KLAC, 8035.T (TEL), ASMJI |
| Benchmarks | SMH, SOXX, ^SOX, ^KS11, ^IXIC, ^TNX (10Y), KRW/USD |

Structural notes: Samsung+SK hynix > 50% of KOSPI → Korean index itself is a memory beta. SKHY trades ~half MU's trailing P/E ("Korea discount") but identical forward (~6x) → forward multiples converge at cycle peaks; track the *ratio* as crowding gauge. Cyclicals die on *deceleration*, never on absolute weakness — monitor second derivatives everywhere.

---

## 5. What the Program Should Predict (formal targets)

1. **Direction**: P(DDR5 16Gb contract QoQ > 0) and P(NAND contract QoQ > 0) for t+1, t+2, t+3 months.
2. **Inflection probability**: P(regime transition within k weeks), regimes ∈ {shortage, maturing, peak, contraction, trough}. Primary observable trigger candidates: N consecutive weeks of flat/down spot with narrowing spot-contract gap; Korea export YoY deceleration >X pts for M consecutive prints; ≥2 majors guiding deceleration.
3. **Street-beat flag**: does TrendForce's own next-quarter forecast get revised up or down at the next publication? (You can systematically out-predict a single vendor's point-in-time forecast by conditioning on data published *after* theirs.)
4. **Consumer layer**: buy/wait advice for RAM/SSD purchases with expected saving horizon (the user's original practical need).

## 6. Modeling Plan (extremely technical)

- **Baselines first**: persistence (next = last), seasonal-naive, TrendForce-forecast-as-given. Any model must beat these out-of-sample or it's noise.
- **Regime layer**: Gaussian HMM (3–5 states) on standardized {DXI returns, Korea YoY accel, equity RS}; Bayesian online changepoint detection on spot series for turn flags; PELT/CUSUM offline for labeling history.
- **Supervised layer**: LightGBM (monotonic constraints where economics dictate) on Tier A–D features → predict target classes; logistic-with-shrinkage as interpretable twin; conformal wrappers for calibrated probabilities (never ship raw GBM probabilities without calibration — isotonic on purged folds).
- **Event layer**: LLM-extracted structured events → event-study abnormal-move estimation → features + standalone rule alerts (fab incident ⇒ immediate spot-volatility flag).
- **Validation protocol**: purged & embargoed walk-forward (embargo ≥ max feature lag, e.g., 40 trading days around earnings windows); label leakage audit for anything using TrendForce forecasts (their publication date ≠ period covered); report Diebold-Mariano vs baselines; keep a permanent holdout = most recent 6 months, touched once.
- **Statistical honesty**: monthly contract history ≈ 240–280 observations total. Weekly spot since ~2001 gives ~1,300. You will NOT achieve Wall Street-grade statistical significance on contract-direction; aim for calibration + early-warning utility (lead-time vs false-alarm ROC), not R².
- **Ops**: daily cron (07:00 KST for Asia close, 17:05 ET for US close); append-only Parquet lake + DuckDB; idempotent ingestors w/ checksums & schema registry; anomaly guards (price jump >30% d/d ⇒ quarantine & alert, likely scraping artifact); Streamlit dashboard + Telegram digest; every prediction logged with features snapshot → automated Brier-score leaderboard vs baselines and vs archived TrendForce forecasts.

## 7. Honest Limitations (read before believing anything)

1. We will not out-trade Jane Street at millisecond horizons — different game entirely. The defensible edge here is **slow, illiquid-information arbitrage**: public-but-obscure data (Korean customs decadal prints, capex event streams, spread microstructure) that moves prices over weeks-months, where nobody's latency advantage matters.
2. TrendForce/IDC/Gartner paid feeds are strictly richer than our free scrapes; our counter-strategy is archiving their free outputs and scoring *them*, plus conditioning on newer public data than their publication stamps.
3. Sample size is small; any backtest over 2001–2026 spans only ~5 full cycles, and the LTA regime change may invalidate pre-2024 dynamics entirely (structural break — weight recent cycles more, say so in the UI).
4. Single-provider dependence: if TrendForce changes site structure, ingestion breaks — build adapters per source with contract tests.
5. Prediction ≠ profit: even correct direction calls don't map to tradable instruments without basis risk analysis (memory equities front-run physical prices by quarters — sometimes the trade is already over when the physical signal confirms).
