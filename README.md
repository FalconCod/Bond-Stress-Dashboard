# Bond Stress Dashboard

A composite stress indicator for the Japanese Government Bond (JGB) market, built from yield curve data and USD/JPY as a cross-market stress proxy. 15 years of daily data (2011-2026), validated against four independently-verifiable historical stress events.

## What it does

Combines three signals into a single daily "stress score":

1. **Yield curve slope** (`10Y − 1Y` yield) — a flattening or inverted curve historically signals stress/recession expectations.
2. **30-day rolling yield volatility** — how erratic day-to-day 10Y yield moves have been recently, independent of direction.
3. **USD/JPY daily % change** — yen weakness and carry-trade unwinds correlate with JGB-specific stress episodes.

Each indicator is z-score normalized (so percentage-point and percent scales become comparable) and averaged into one composite score, with slope's sign flipped so all three indicators agree that a higher score always means more stress.

## Why JGB, not Indian G-Secs

The project started targeting Indian G-Sec bonds via RBI's DBIE portal. JGB data (Japan's Ministry of Finance, `data.mof.go.jp`) turned out to be cleanly downloadable as CSV with no login friction and a much longer clean history, so the analysis pivoted there. Same methodology, different market.

## Data sources

- **JGB yields**: [Ministry of Finance Japan](https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/), official historical interest rate data, maturities 1Y-40Y, daily, 1974-present. Only 1Y and 10Y are used.
- **USD/JPY**: pulled live via `yfinance` (ticker `JPY=X`), daily close.
- **Analysis window**: 2011-2026, chosen to span three distinct BOJ policy regimes — pre-YCC easing (2011-2016), Yield Curve Control (2016-2022), and the YCC unwind / fiscal-driven yield surge (2022-2026).

## Findings

- **2019 curve inversion**: 8 trading days of negative slope in Aug-Sep 2019, both legs negative — a brief global stress episode (US-China trade war scare) absorbed by JGB as a safe haven, not a Japan-specific shock.
- **Correlation check**: slope vs volatility = 0.47 (related but distinct), slope vs USD/JPY change ≈ 0.02 (independent) — no indicator needed down-weighting before combining.
- **Historical validation**: the composite score was checked against 4 named events picked in advance — the 2013 BOJ QQE "bazooka" launch, the 2019 inversion, the 2020 COVID crash, and the 2023 BOJ YCC band-widening surprise. All four land in the **top 2% of all 3,751 trading days** in the dataset, with score peaks landing within days to two weeks of the actual event date.

Full methodology, formulas, and data quality checks are in [`notes.md`](notes.md).

## Repo structure

```
src/
  data_loader.py   # loads + cleans JGB yield CSV
  fx_loader.py     # pulls USD/JPY via yfinance
  merge_data.py    # joins data, computes indicators, z-scores, composite score, plots
data/raw/          # source JGB CSV
notebooks/         # generated plots (slope, volatility, correlation, composite score)
notes.md           # full methodology + findings log
```

## How to run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m src.merge_data
```

Prints indicator summaries, correlation matrix, top-10 highest-stress days, and the historical validation table, and saves all plots to `notebooks/`.

## Status

Data pipeline, all three indicators, correlation check, composite score, and historical validation are complete. Streamlit dashboard is next.
