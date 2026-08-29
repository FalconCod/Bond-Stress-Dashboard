import streamlit as st

from src.data import load_curve_data
from src.charts import ns_factor_chart, ns_fit_comparison_chart
from src.theme import get_theme
from src.ui import (
    inject_css,
    render_theme_toggle_sidebar,
    render_page_header,
    render_kpi_row,
    render_chart_panel,
    render_chart_grid,
    render_footer,
)

SPARK_DAYS = 30

selected_theme = render_theme_toggle_sidebar(get_theme(st.session_state.theme_name))
if selected_theme != st.session_state.theme_name:
    st.session_state.theme_name = selected_theme
    st.query_params["theme"] = selected_theme
    st.rerun()

theme = get_theme(st.session_state.theme_name)
inject_css(theme)

raw_df, betas_df = load_curve_data()
latest = betas_df.iloc[-1]
prev = betas_df.iloc[-2]

render_page_header(
    theme, "YIELD CURVE MODEL",
    "Nelson-Siegel factor decomposition &middot; 2Y-30Y JGB",
    raw_df.index.min().date(), raw_df.index.max().date(),
)

kpis = [
    dict(
        label="Level (b0)",
        value=f"{latest['ns_level']:.3f}",
        delta=f"{'+' if latest['ns_level'] - prev['ns_level'] >= 0 else ''}"
              f"{latest['ns_level'] - prev['ns_level']:.3f} vs prior day",
        color=theme["blue"],
        series=betas_df["ns_level"].tail(SPARK_DAYS),
    ),
    dict(
        label="Slope (b1)",
        value=f"{latest['ns_slope']:.3f}",
        delta=f"{'+' if latest['ns_slope'] - prev['ns_slope'] >= 0 else ''}"
              f"{latest['ns_slope'] - prev['ns_slope']:.3f} vs prior day",
        color=theme["cyan"],
        series=betas_df["ns_slope"].tail(SPARK_DAYS),
    ),
    dict(
        label="Curvature (b2)",
        value=f"{latest['ns_curvature']:.3f}",
        delta=f"{'+' if latest['ns_curvature'] - prev['ns_curvature'] >= 0 else ''}"
              f"{latest['ns_curvature'] - prev['ns_curvature']:.3f} vs prior day",
        color=theme["amber"],
        series=betas_df["ns_curvature"].tail(SPARK_DAYS),
    ),
    dict(
        label="Fit RMSE (pp)",
        value=f"{latest['ns_rmse']:.4f}",
        delta=f"mean {betas_df['ns_rmse'].mean():.4f} &middot; lambda={latest['ns_lambda']:.2f}",
        color=theme["green"] if latest["ns_rmse"] < betas_df["ns_rmse"].quantile(0.75) else theme["amber"],
        series=betas_df["ns_rmse"].tail(SPARK_DAYS),
    ),
]
render_kpi_row(theme, kpis)

st.write("")

sample_dates = [
    str(raw_df.index.min().date()),
    str(betas_df["ns_rmse"].idxmax().date()),
    str(raw_df.index.max().date()),
]
render_chart_panel(
    f"ACTUAL vs FITTED CURVE — {sample_dates[0]} (early), {sample_dates[1]} (worst fit), {sample_dates[2]} (latest)",
    ns_fit_comparison_chart(raw_df, betas_df, sample_dates, theme),
    None,
)

st.write("")

panels = [
    ("LEVEL (b0)", ns_factor_chart(betas_df, "ns_level", "level", "blue", theme), kpis[0]["color"]),
    ("SLOPE (b1)", ns_factor_chart(betas_df, "ns_slope", "slope", "cyan", theme), kpis[1]["color"]),
    ("CURVATURE (b2)", ns_factor_chart(betas_df, "ns_curvature", "curvature", "amber", theme), kpis[2]["color"]),
    ("FIT RMSE (pp)", ns_factor_chart(betas_df, "ns_rmse", "rmse", "green", theme), kpis[3]["color"]),
]
render_chart_grid(panels)

render_footer()
