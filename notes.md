# Bond Stress Dashboard — Project Notes

## What this project does
Builds a composite stress indicator for the Japanese Government Bond (JGB)
market, using yield curve data and USD/JPY as a cross-market stress proxy.

## Data sources
- **JGB yields**: Ministry of Finance Japan, official historical interest
  rate data (data.mof.go.jp), maturities 1Y-40Y, daily, 1974-present.
  Used columns: 1Y, 10Y only.
- **USD/JPY**: pulled via yfinance (ticker JPY=X), daily close.

## Analysis window
2011-2026 (15 years). Chosen to cover multiple distinct policy regimes:
pre-YCC easing (2011-2016), Yield Curve Control / negative rates
(2016-2022ish), YCC unwind and fiscal-driven yield surge (2022-2026).
Older data (1974-2011) exists in the raw file but excluded — different
monetary regime, not comparable to current conditions.

## Indicator 1: Yield curve slope
Formula: slope = 10Y yield − 1Y yield (in percentage points), computed
per trading day.
- Positive slope = normal curve (long end pays more, as expected).
- Near-zero/negative = flattened/inverted curve, historically a
  stress/recession-expectation signal.
- Verified visually: plotted 1Y and 10Y raw yields together
(notebooks/raw_yields_plot.png) — lines visibly cross during the
Aug-Sep 2019 window, confirming the inversion is real, not a
calculation artifact.

### Finding: Aug-Sep 2019 inversion
8 trading days with negative slope, both 1Y and 10Y yields negative.
Both legs negative + brief window = global stress absorbed by JGB as
safe-haven, not Japan-specific event. Timing matches the 2019 US-China
trade war escalation / global recession scare (US 2Y-10Y also inverted
around this time). Magnitude shallow (~-0.02 max) — consistent with a
scare, not a crisis.

### Visual regime read (full 2011-2026 plot)
1. 2011-2016: steady decline (~1.1 to near-zero) — pre-YCC easing cycle.
2. 2016-2022: flat, suppressed, choppy near-zero — YCC actively capping
   the curve. 2019 inversion is a sharp anomaly *inside* this period,
   not the start of a trend.
3. 2022-2026: sustained, accelerating climb to 15-year highs (~1.65) —
   YCC unwind + current fiscal-spending-driven yield surge.

## Credit/stress leg: USD/JPY
Not derived from bond data — separate currency market, joined in by
date. Rationale: yen weakness / carry-trade unwinds correlate with JGB
stress episodes specifically for Japan (unlike a generic credit-spread
proxy). USD/JPY moved ~81 (2011) to ~162 (2026) over the window — yen
roughly halved.

## Data pipeline (technical)
- `src/data_loader.py`: loads JGB CSV, skips junk header row, treats
  `-` as NaN, explicit date parsing, filters to analysis window.
- `src/fx_loader.py`: pulls USD/JPY via yfinance, flattens MultiIndex
  column bug present in current yfinance version.
- `src/merge_data.py`: inner-joins JGB + FX on date (drops mismatched
  calendar dates), computes slope, detects/prints inversions, plots.

## Data quality checks performed
- JGB: all yield columns confirmed float64 (no leftover string
  artifacts from `-` placeholder).
- Zero missing values, 1Y and 10Y, full 2011-2026 window.
- Zero missing values, USD/JPY, full window.
- Merged dataset: 3781 rows, zero NaNs across all columns.

## Open items / next steps
- [ ] Rolling 30-day yield volatility (second indicator)
- [ ] Correlation check between slope, volatility, USD/JPY before
      deciding composite weights (don't assume independence)
- [ ] Z-score normalization
- [ ] Composite score (equal weight vs PCA-derived, compare both)
- [ ] Streamlit dashboard