import streamlit as st

from src.merge_data import (
    build_merged_dataset,
    add_slope,
    add_volatility,
    add_fx_change,
)
from src.charts import yields_chart, slope_chart, volatility_chart, usdjpy_chart
from src.theme import get_theme
from src.ui import (
    inject_css,
    status_color,
    render_header,
    render_status_legend,
    render_kpi_row,
    render_chart_grid,
    render_footer,
)

SPARK_DAYS = 30

st.set_page_config(page_title="JGB Bond Stress Dashboard", layout="wide")

if "theme_name" not in st.session_state:
    # Persist across a hard refresh via the URL, since st.session_state
    # resets on a new browser session but query params survive a reload.
    query_theme = st.query_params.get("theme")
    st.session_state.theme_name = query_theme if query_theme in ("light", "dark") else "dark"
    st.query_params["theme"] = st.session_state.theme_name

theme = get_theme(st.session_state.theme_name)
inject_css(theme)


@st.cache_data
def load_data():
    df = build_merged_dataset()
    df = add_slope(df)
    df = add_volatility(df)
    df = add_fx_change(df)
    return df


df = load_data()
latest = df.iloc[-1]
prev = df.iloc[-2]

selected_theme = render_header(theme, df.index.min().date(), df.index.max().date())
if selected_theme != st.session_state.theme_name:
    st.session_state.theme_name = selected_theme
    st.query_params["theme"] = selected_theme
    st.rerun()

render_status_legend(theme)

kpis = [
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

panels = [
    ("RAW YIELDS: 1Y vs 10Y", yields_chart(df, theme), None),
    ("YIELD CURVE SLOPE (10Y − 1Y)", slope_chart(df, theme), kpis[0]["color"]),
    ("30-DAY ROLLING VOLATILITY", volatility_chart(df, theme), kpis[1]["color"]),
    ("USD/JPY", usdjpy_chart(df, theme), kpis[2]["color"]),
]
render_chart_grid(panels)

render_footer()
