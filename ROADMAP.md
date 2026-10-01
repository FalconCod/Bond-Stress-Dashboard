# JGB Bond Stress Monitor — Roadmap

Single project, full focus. Originally planned as a 13-day Streamlit
dashboard; rebuilt from Day 8 onward as a genuine quant-finance research
project — curve-factor modeling, a regime-switching model instead of
hardcoded thresholds, forward-looking volatility, and a rigorous
out-of-sample backtest — because the original design (2-point slope →
z-score → fixed RGB bands) had no real modeling decision in it.

Branch: `stress-analyser`. One commit per working day, no exceptions.

## Rigor amendments (apply to every day below, not just where noted)

- **Walk-forward, not in-sample validation.** Any claim that a
  model "caught" a known stress event must be checked by fitting on
  data *before* that event and classifying forward into unseen data —
  not by fitting on the whole sample and then pointing at the spike.
  Applies hardest to Day 12 (backtest) and Day 10 (regime labels).
- **Diagnostics, not just "it ran."** Every statistical model ships
  with the check that justifies it: HMM state count via BIC/AIC (not
  picked by feel), GARCH residuals via Ljung-Box (confirms no leftover
  autocorrelation), stationarity via ADF before trusting a VAR/Granger
  result.
- **Benchmark against the naive baseline.** A model's score only means
  something next to a simpler alternative — e.g. the NS/HMM pipeline
  compared against plain realized vol or the original 2-point slope.
  If the added complexity doesn't beat the baseline, that's a finding
  worth writing down, not hiding.
- **Model documentation, not just a README.** Real institutions (SR
  11-7 model risk guidance, the standard most US banks including
  Morgan Stanley operate under) require every model to carry documented
  purpose, assumptions, limitations, validation evidence, and a
  monitoring plan before use. Day 23 produces that document, not a
  casual writeup.
- **"So what."** The output isn't just "stress score is high" — note
  the implied action (e.g. reduce duration, widen hedges) and an honest
  line on transaction-cost/implementability if someone tried to trade
  on it.

## Status

| Day | Deliverable | Status | Notes |
|---|---|---|---|
| 0 | Repo setup, data source scouting | ✅ Done | Pivoted from Indian G-Sec to JGB — cleaner data access |
| 1 | Raw yield data + loader | ✅ Done | `src/data_loader.py` |
| 2 | Clean data, save clean CSV | ⚠️ Partial | Cleaning is in-memory; `data/clean/` still unpersisted |
| 3 | 3 stress indicators + formulas | ✅ Done | Slope, 30d volatility, USD/JPY |
| 4 | Z-score + composite score | ✅ Done | Slope sign correctly flipped in the formula |
| 5 | Historical validation | ✅ Done | 4 real events, top 2% of days — **in-sample**, see Day 12 amendment |
| 6 | Streamlit skeleton + raw charts | ✅ Done, exceeded | Terminal-style theming, sparklines, KPI cards, zoom controls |
| 7 | Composite score chart + thresholds | ✅ Done | Green/amber/red bands, theme-aware |
| 8 | Nelson-Siegel curve fitting | ✅ Done | λ calibrated once (Diebold-Li), β0/β1/β2 daily OLS; mean fit RMSE ≈ 3.9bp; exact-recovery unit tests |
| — | Multi-page app, resilience, theming fixes | ✅ Done | `st.navigation`, yfinance disk-cache fallback, 3 real UI bugs found + fixed |
| 9 | NS-factor-based indicators | ⬜ Next | Compare curve-derived slope/curvature vs original 2-point slope |
| 10 | HMM regime detection | ⬜ Not started | **Amended**: justify state count via BIC/AIC; regime labels validated walk-forward |
| 11 | GARCH volatility forecast | ⬜ Not started | **Amended**: Ljung-Box on residuals before trusting the fit |
| 12 | Backtest engine | ⬜ Not started | **Amended**: out-of-sample / walk-forward, not in-sample event-matching; real precision/recall/lead-time numbers |
| 13 | Cross-market spillover (VAR/Granger) | ⬜ Not started | **Amended**: ADF stationarity check before VAR |
| 14 | Package refactor + tests | ⬜ Not started | `config.yaml`, broader `tests/` |
| 15 | FastAPI service layer | ⬜ Not started | Streamlit becomes a client of the API, not the model |
| 16 | DuckDB backend | ⬜ Not started | Replaces flat CSVs |
| 17 | Automated data refresh | ⬜ Not started | GitHub Actions scheduled job |
| 18 | Docker + CI | ⬜ Not started | pytest on every push |
| 19 | Sensitivity analysis | ⬜ Not started | **Amended**: add benchmark comparison vs naive baseline, not just weight perturbation |
| 20 | UI overhaul | ⬜ Not started | Regime-colored bands, NS/GARCH/spillover views, "why this regime" explainability panel |
| 21 | Edge-case hardening | ⬜ Not started | Missing dates, curve-fit non-convergence |
| 22 | Deploy | ⬜ Not started | Streamlit Cloud (UI) + Render/Railway (API) |
| 23 | Model documentation + methodology writeup | ⬜ Not started | **New scope**: SR 11-7-style doc (purpose, assumptions, limitations, validation, monitoring plan), not just a research note |
| 24 | README + demo | ⬜ Not started | Walkthrough defends model choices; include the "so what" / implementability note |

## Priority if time runs short

Compress infra first (Days 15-18, 22), keep modeling depth intact (Days
8-13, 19, 23) — infra is a smaller signal than modeling judgment for a
quant/rates seat.
