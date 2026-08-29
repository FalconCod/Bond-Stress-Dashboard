"""Nelson-Siegel yield curve fitting.

y(tau) = b0 + b1 * slope_loading(tau) + b2 * curvature_loading(tau)

b0 (level), b1 (slope), b2 (curvature) are the three latent factors that
summarize the whole curve shape at each point in time. lambda controls
where the curvature loading peaks and is calibrated once (not refit
daily) — see calibrate_lambda for why.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

TENORS = np.array([2, 5, 10, 20, 30])  # years, must match columns available in the data


def ns_loadings(tau, lam):
    """Nelson-Siegel basis matrix: columns are [level, slope, curvature] loadings."""
    tau = np.asarray(tau, dtype=float)
    x = tau / lam
    slope_loading = (1 - np.exp(-x)) / x
    curvature_loading = slope_loading - np.exp(-x)
    return np.column_stack([np.ones_like(tau), slope_loading, curvature_loading])


def fit_betas(yields, tau, lam):
    """OLS fit of [b0, b1, b2] for one curve snapshot, given a fixed lambda."""
    X = ns_loadings(tau, lam)
    betas, *_ = np.linalg.lstsq(X, yields, rcond=None)
    return betas


def ns_curve(tau, betas, lam):
    """Reconstruct fitted yields at maturities tau from betas + lambda."""
    X = ns_loadings(tau, lam)
    return X @ betas


def _fit_sse(lam, avg_yields, tau):
    betas = fit_betas(avg_yields, tau, lam)
    fitted = ns_curve(tau, betas, lam)
    return np.sum((fitted - avg_yields) ** 2)


def calibrate_lambda(df, tenors=TENORS):
    """Calibrate a single lambda from the sample-average yield curve.

    Refitting lambda nonlinearly every day, from only 5 tenor points, is
    unstable — it would fit day-to-day noise in the decay rate rather
    than genuine curve shape. Fixing lambda once (Diebold & Li, 2006)
    turns the daily fit into a stable linear regression for b0/b1/b2.
    """
    cols = [f"{t}Y" for t in tenors]
    avg_yields = df[cols].mean().values
    result = minimize_scalar(_fit_sse, bounds=(0.1, 10), method="bounded", args=(avg_yields, tenors))
    return result.x


def fit_ns_daily(df, tenors=TENORS, lam=None):
    """Fit b0 (level), b1 (slope), b2 (curvature) for every row in df.

    Vectorized: one lstsq call solves all days at once rather than
    looping, since lambda (and therefore the loading matrix X) is the
    same for every day once calibrated.
    """
    if lam is None:
        lam = calibrate_lambda(df, tenors)
    cols = [f"{t}Y" for t in tenors]
    X = ns_loadings(tenors, lam)  # (n_tenors, 3)
    yields = df[cols].values  # (n_days, n_tenors)
    betas, *_ = np.linalg.lstsq(X, yields.T, rcond=None)  # (3, n_days)
    result = pd.DataFrame(
        betas.T, columns=["ns_level", "ns_slope", "ns_curvature"], index=df.index
    )
    result["ns_lambda"] = lam
    return result


def fit_quality(df, betas_df, tenors=TENORS):
    """RMSE of fitted vs actual yields per day, to quantify fit quality."""
    cols = [f"{t}Y" for t in tenors]
    lam = betas_df["ns_lambda"].iloc[0]
    X = ns_loadings(tenors, lam)
    fitted = betas_df[["ns_level", "ns_slope", "ns_curvature"]].values @ X.T
    actual = df[cols].values
    return pd.Series(
        np.sqrt(np.mean((fitted - actual) ** 2, axis=1)), index=df.index, name="ns_rmse"
    )
