import streamlit as st

from src.data import load_indicator_data
from src.charts import yields_chart, slope_chart, volatility_chart, usdjpy_chart, composite_score_chart
from src.theme import get_theme
from src.ui import (
    inject_css,
    status_color,
    render_theme_toggle_sidebar,
    render_page_header,
    render_status_legend,
    render_kpi_row,
    render_chart_panel,
    render_chart_grid,
    render_footer,
)

SPARK_DAYS = 30
STRESS_THRESHOLDS = (0.5, 1.5)

selected_theme = render_theme_toggle_sidebar(get_theme(st.session_state.theme_name))
if selected_theme != st.session_state.theme_name:
    st.session_state.theme_name = selected_theme
    st.query_params["theme"] = selected_theme
    st.rerun()

theme = get_theme(st.session_state.theme_name)
inject_css(theme)

df = load_indicator_data()
latest = df.iloc[-1]
prev = df.iloc[-2]

render_page_header(
    theme, "JGB BOND STRESS MONITOR",
    "Japanese Government Bond &middot; 1Y / 10Y &middot; USD/JPY",
    df.index.min().date(), df.index.max().date(),
)
render_status_legend(theme)

kpis = [
    dict(
        label="Composite Stress Score",
        value=f"{latest['stress_score']:.3f}",
        delta=f"{'+' if latest['stress_score'] - prev['stress_score'] >= 0 else ''}"
              f"{latest['stress_score'] - prev['stress_score']:.3f} vs prior day",
        color=status_color(theme, latest["stress_score"], thresholds=STRESS_THRESHOLDS),
        series=df["stress_score"].tail(SPARK_DAYS),
    ),
    dict(
        label="10Y-1Y Slope (pp)",
        value=f"{latest['slope_10y_1y']:.3f}",
        delta=f"{'+' if latest['slope_10y_1y'] - prev['slope_10y_1y'] >= 0 else ''}"
              f"{latest['slope_10y_1y'] - prev['slope_10y_1y']:.3f} vs prior day",
        color=theme["red"] if latest["slope_10y_1y"] < 0 else theme["green"],
        series=df["slope_10y_1y"].tail(SPARK_DAYS),
    ),
    dict(
        label="30D Volatility (pp)",
        value=f"{latest['vol_30d']:.4f}",
        delta=f"mean {df['vol_30d'].mean():.4f}",
        color=status_color(theme, latest["vol_30d"] * 20),
        series=df["vol_30d"].tail(SPARK_DAYS),
    ),
    dict(
        label="USD/JPY Daily Chg (%)",
        value=f"{latest['usdjpy_change']:+.3f}",
        delta=f"USD/JPY {latest['USDJPY']:.2f}",
        color=status_color(theme, latest["usdjpy_change"], thresholds=(0.5, 1.2)),
        series=df["USDJPY"].tail(SPARK_DAYS),
    ),
]
render_kpi_row(theme, kpis)

st.write("")

render_chart_panel(
    "COMPOSITE STRESS SCORE (Z-SCORE AVG, GREEN/AMBER/RED THRESHOLD BANDS)",
    composite_score_chart(df, theme, thresholds=STRESS_THRESHOLDS),
    kpis[0]["color"],
)

st.write("")

panels = [
    ("RAW YIELDS: 1Y vs 10Y", yields_chart(df, theme), None),
    ("YIELD CURVE SLOPE (10Y − 1Y)", slope_chart(df, theme), kpis[1]["color"]),
    ("30-DAY ROLLING VOLATILITY", volatility_chart(df, theme), kpis[2]["color"]),
    ("USD/JPY", usdjpy_chart(df, theme), kpis[3]["color"]),
]
render_chart_grid(panels)

render_footer()
