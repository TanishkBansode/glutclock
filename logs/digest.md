# GlutClock Daily Digest — 2026-08-25 21:43 UTC

## Verdict
- **Cycle regime:** `contraction` — memory equities in deep drawdown (-30%)
- **Consumer advice:** **NEUTRAL** — Korea export YoY decelerating (-37.7 pts): supply catching up within quarters
- **Proxy model** P(memory equities up next 5d): **56%** (test Brier 0.2466 vs majority acc 0.528, asof 2026-08-25)

## Key indicators
| Indicator | Value |
|---|---|
| DDR5 16Gb spot (USD) | 54.17 |
| DDR5 spot chg 7d (%) | - |
| NAND 512Gb TLC spot (USD) | 21.21 |
| NAND 512Gb chg 7d (%) | - |
| DDR5 eTT discount (%) | 56.20 |
| DDR4/DDR5 price ratio | 1.67 |
| Spot breadth (% items up) | 70.00 |
| Korea D10 semi exports YoY (%) | 155.40 |
| Korea YoY acceleration (pts) | -37.70 |
| Memory basket momentum 20d | 0.15 |
| Memory basket momentum 60d | -0.12 |
| Memory basket drawdown from 250d high | -0.30 |
| Memory basket vs SOX 60d excess | 0.10 |
| SOX momentum 20d | 0.05 |
| US 10Y yield (%) | 4.64 |

## Today's predictions (logged to ledger)
| Target | Horizon | Model P(up) | Constant baseline | Note |
|---|---|---|---|---|
| T1_ddr5_spot_dir_7d | 7d | - | 0.50 | momentum heuristic; learned model pending 60+ days of physical prices |
| T2_nand512_spot_dir_7d | 7d | - | 0.50 | momentum heuristic; learned model pending 60+ days of physical prices |

## Alerts
- ⚠️ Korea D10 semi-export YoY decelerating fast (-37.7 pts)

## Latest TrendForce memory press items (archived)
- [2026-08-25] Memory Prices Soar; DRAM and NAND Flash to Account for 68% of Major CSP CapEx in 2027, Says TrendForce… 
- [2026-08-18] Combined Revenue of Top Five NAND Flash Brands Rises 77% QoQ in 2Q26; Micron Moves Up to Third Place, Says TrendForce… 

## Source status (this run)
| Source | Status | Rows | Detail |
|---|---|---|---|
| markets | ok | 20318 | total=20376 new_days=0 src=yfinance |
| trendforce | ok | 14 | flagged=0 total_rows=56 |
| korea_customs | ok | 4 | manual+seed; automate via data.go.kr key in v1 |
| press | ok | 1 | total=2 |

---
*Baselines are permanent: a model that cannot beat them is labeled as such. Physical-price history starts at system deployment; equity features use deep history immediately.*