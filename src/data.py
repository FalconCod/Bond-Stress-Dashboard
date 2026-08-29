"""Shared, cached data loaders used by every page. Centralized so the
2Y/5Y/10Y/20Y/30Y load + Nelson-Siegel fit happens once per session,
not once per page."""

import streamlit as st

from src.data_loader import load_jgb_data, filter_window
from src.merge_data import (
    build_merged_dataset,
    add_slope,
    add_volatility,
    add_fx_change,
    add_zscores,
    add_composite_score,
)
from src.curve import TENORS, calibrate_lambda, fit_ns_daily, fit_quality


def _stop_with_error(message):
    st.error(message)
    st.stop()


@st.cache_data
def load_indicator_data():
    """1Y/10Y-based slope, volatility, USD/JPY, composite score — the
    Day 1-7 pipeline, unchanged."""
    try:
        df = build_merged_dataset()
    except Exception as exc:
        _stop_with_error(
            f"Could not load market data (USD/JPY fetch failed: {exc}). "
            "This is usually a temporary yfinance rate limit — wait a "
            "few minutes and reload."
        )
    if df.empty:
        _stop_with_error(
            "Merged JGB + USD/JPY dataset came back empty — the USD/JPY "
            "fetch likely failed silently (yfinance rate limit) and no "
            "cached fallback exists yet. Wait a few minutes and reload."
        )
    df = add_slope(df)
    df = add_volatility(df)
    df = add_fx_change(df)
    df = df.dropna(subset=["slope_10y_1y", "vol_30d", "usdjpy_change"])
    df = add_zscores(df)
    df = add_composite_score(df)
    return df


@st.cache_data
def load_curve_data(start_year=2011):
    """Full multi-tenor JGB curve (2Y-30Y) plus daily Nelson-Siegel fit."""
    raw = load_jgb_data()
    raw = filter_window(raw, start_year=start_year)
    raw = raw.set_index("Date")
    cols = [f"{t}Y" for t in TENORS]
    raw = raw.dropna(subset=cols)
    if raw.empty:
        _stop_with_error("JGB curve data came back empty after dropping missing tenors.")

    lam = calibrate_lambda(raw)
    betas = fit_ns_daily(raw, lam=lam)
    betas["ns_rmse"] = fit_quality(raw, betas)
    return raw, betas
