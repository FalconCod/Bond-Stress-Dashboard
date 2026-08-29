"""Unit tests for src/curve.py (Nelson-Siegel curve fitting)."""

import numpy as np
import pandas as pd
import pytest

from src.curve import (
    TENORS,
    ns_loadings,
    fit_betas,
    ns_curve,
    calibrate_lambda,
    fit_ns_daily,
    fit_quality,
)


def test_loadings_level_is_always_one():
    loadings = ns_loadings(TENORS, lam=1.5)
    assert loadings[:, 0].tolist() == pytest.approx([1.0] * len(TENORS))


def test_loadings_short_maturity_limit():
    # As tau -> 0, slope loading -> 1 and curvature loading -> 0
    # (L'Hopital on (1-e^-x)/x as x -> 0).
    loadings = ns_loadings(np.array([1e-6]), lam=1.5)
    assert loadings[0, 1] == pytest.approx(1.0, abs=1e-4)
    assert loadings[0, 2] == pytest.approx(0.0, abs=1e-4)


def test_loadings_long_maturity_limit():
    # As tau -> infinity, both slope and curvature loadings -> 0.
    loadings = ns_loadings(np.array([1000.0]), lam=1.5)
    assert loadings[0, 1] == pytest.approx(0.0, abs=2e-3)
    assert loadings[0, 2] == pytest.approx(0.0, abs=2e-3)


def test_fit_betas_recovers_known_parameters_exactly():
    # Generate a curve FROM known betas, then check the fit recovers them.
    # This is the strongest test here: it proves the fit isn't just
    # "close", it's mathematically exact on noiseless, consistent data.
    true_betas = np.array([1.2, -0.8, 0.4])
    lam = 1.5
    synthetic_yields = ns_curve(TENORS, true_betas, lam)

    fitted_betas = fit_betas(synthetic_yields, TENORS, lam)
    assert fitted_betas == pytest.approx(true_betas, abs=1e-8)


def test_ns_curve_reconstruction_matches_fit():
    true_betas = np.array([1.0, 0.5, -0.3])
    lam = 1.5
    yields = ns_curve(TENORS, true_betas, lam)
    fitted_betas = fit_betas(yields, TENORS, lam)
    reconstructed = ns_curve(TENORS, fitted_betas, lam)
    assert reconstructed == pytest.approx(yields, abs=1e-8)


def test_calibrate_lambda_returns_value_within_bounds():
    dates = pd.date_range("2020-01-01", periods=30, freq="B")
    true_betas = np.array([1.0, -0.5, 0.2])
    true_lam = 1.4
    cols = [f"{t}Y" for t in TENORS]
    yields = np.tile(ns_curve(TENORS, true_betas, true_lam), (30, 1))
    df = pd.DataFrame(yields, columns=cols, index=dates)

    lam = calibrate_lambda(df)
    assert 0.1 <= lam <= 10
    # On a perfectly flat (noiseless, repeated) curve, calibration should
    # recover the true lambda closely.
    assert lam == pytest.approx(true_lam, abs=0.05)


def test_fit_ns_daily_shape_and_recovery():
    dates = pd.date_range("2020-01-01", periods=5, freq="B")
    cols = [f"{t}Y" for t in TENORS]
    lam = 1.5
    true_betas_per_day = np.array([
        [1.0, 0.5, -0.2],
        [1.1, 0.4, -0.1],
        [0.9, 0.6, -0.3],
        [1.0, 0.5, -0.2],
        [1.2, 0.3, 0.0],
    ])
    yields = np.array([ns_curve(TENORS, b, lam) for b in true_betas_per_day])
    df = pd.DataFrame(yields, columns=cols, index=dates)

    result = fit_ns_daily(df, lam=lam)
    assert list(result.columns) == ["ns_level", "ns_slope", "ns_curvature", "ns_lambda"]
    assert len(result) == 5
    fitted = result[["ns_level", "ns_slope", "ns_curvature"]].values
    assert fitted == pytest.approx(true_betas_per_day, abs=1e-8)
    assert (result["ns_lambda"] == lam).all()


def test_fit_quality_near_zero_for_exact_data():
    dates = pd.date_range("2020-01-01", periods=3, freq="B")
    cols = [f"{t}Y" for t in TENORS]
    lam = 1.5
    true_betas = np.array([1.0, 0.5, -0.2])
    yields = np.tile(ns_curve(TENORS, true_betas, lam), (3, 1))
    df = pd.DataFrame(yields, columns=cols, index=dates)

    betas_df = fit_ns_daily(df, lam=lam)
    rmse = fit_quality(df, betas_df)
    assert (rmse < 1e-8).all()
