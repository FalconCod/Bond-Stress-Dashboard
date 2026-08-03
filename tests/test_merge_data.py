"""
Unit tests for src/merge_data.py.

These operate on small synthetic DataFrames rather than the real pipeline
(build_merged_dataset), so they run fast, deterministically, and without
a network call to yfinance or a read of data/raw/jgbcme_all.csv.
"""

import numpy as np
import pandas as pd
import pytest

from src.merge_data import (
    add_slope,
    add_volatility,
    add_fx_change,
    add_zscores,
    add_composite_score,
    compute_correlation,
    validate_against_known_events,
)


def make_dates(n, start="2020-01-01"):
    return pd.date_range(start, periods=n, freq="B")


def test_add_slope_is_10y_minus_1y():
    df = pd.DataFrame({"1Y": [0.1, 0.2, -0.1], "10Y": [1.0, 0.5, -0.2]})
    result = add_slope(df)
    assert result["slope_10y_1y"].tolist() == pytest.approx([0.9, 0.3, -0.1])


def test_add_slope_does_not_mutate_input():
    df = pd.DataFrame({"1Y": [0.1], "10Y": [1.0]})
    add_slope(df)
    assert "slope_10y_1y" not in df.columns


def test_add_volatility_first_window_rows_are_nan():
    n = 40
    window = 30
    df = pd.DataFrame({"10Y": np.linspace(1.0, 1.39, n)}, index=make_dates(n))
    result = add_volatility(df, window=window)
    # yield_change is NaN for row 0, so the rolling std needs `window` more
    # rows before it has enough history -> first `window` vol_30d rows NaN.
    assert result["vol_30d"].isna().sum() == window
    assert result["vol_30d"].iloc[window:].notna().all()


def test_add_volatility_zero_for_constant_daily_change():
    n = 40
    df = pd.DataFrame({"10Y": np.linspace(1.0, 1.39, n)}, index=make_dates(n))
    result = add_volatility(df, window=30)
    # Linearly spaced yields => constant daily change => zero rolling std.
    assert result["vol_30d"].dropna().tolist() == pytest.approx([0.0] * 10, abs=1e-9)


def test_add_fx_change_is_percent_change():
    df = pd.DataFrame({"USDJPY": [100.0, 101.0, 99.99]})
    result = add_fx_change(df)
    assert result["usdjpy_change"].iloc[1] == pytest.approx(1.0)
    assert result["usdjpy_change"].iloc[2] == pytest.approx(-1.0)
    assert pd.isna(result["usdjpy_change"].iloc[0])


def test_add_zscores_normalizes_to_mean_zero_std_one():
    n = 50
    rng = np.random.default_rng(seed=0)
    df = pd.DataFrame({
        "slope_10y_1y": rng.normal(0.5, 0.2, n),
        "vol_30d": rng.uniform(0.01, 0.05, n),
        "usdjpy_change": rng.normal(0, 0.5, n),
    })
    result = add_zscores(df)
    for col in ("z_slope", "z_vol", "z_fx"):
        assert result[col].mean() == pytest.approx(0.0, abs=1e-9)
        assert result[col].std() == pytest.approx(1.0, abs=1e-9)


def test_composite_score_flips_slope_sign():
    # A calm, steep curve (high z_slope) must PULL the score down, not up,
    # since low/negative slope is the stress signal, not high slope.
    df = pd.DataFrame({"z_slope": [2.0], "z_vol": [0.0], "z_fx": [0.0]})
    result = add_composite_score(df)
    assert result["stress_score"].iloc[0] == pytest.approx(-2.0 / 3)


def test_composite_score_matches_manual_average():
    df = pd.DataFrame({"z_slope": [-1.0], "z_vol": [2.0], "z_fx": [1.0]})
    result = add_composite_score(df)
    # -(-1) + 2 + 1 = 4, divided by 3
    assert result["stress_score"].iloc[0] == pytest.approx(4.0 / 3)


def test_compute_correlation_diagonal_is_one():
    df = pd.DataFrame({
        "slope_10y_1y": [1, 2, 3, 4, 5],
        "vol_30d": [5, 4, 3, 2, 1],
        "usdjpy_change": [1, 3, 2, 5, 4],
    })
    corr = compute_correlation(df)
    assert np.diag(corr).tolist() == pytest.approx([1.0, 1.0, 1.0])


def test_compute_correlation_detects_perfect_negative_relationship():
    df = pd.DataFrame({
        "slope_10y_1y": [1, 2, 3, 4, 5],
        "vol_30d": [5, 4, 3, 2, 1],
        "usdjpy_change": [10, 20, 15, 25, 30],
    })
    corr = compute_correlation(df)
    assert corr.loc["slope_10y_1y", "vol_30d"] == pytest.approx(-1.0)


def test_validate_against_known_events_finds_the_planted_spike():
    n = 100
    dates = make_dates(n)
    scores = pd.Series(0.1, index=dates)
    spike_date = dates[50]
    scores.loc[spike_date] = 5.0
    df = pd.DataFrame({"stress_score": scores})

    events = [(str(spike_date.date()), "planted spike")]
    result = validate_against_known_events(df, events=events, window_days=5)

    assert len(result) == 1
    assert result.iloc[0]["peak_score"] == pytest.approx(5.0)
    assert result.iloc[0]["peak_date"] == spike_date.date()
    # It's the single highest score in the whole series -> 99th+ percentile.
    assert result.iloc[0]["percentile"] > 95
