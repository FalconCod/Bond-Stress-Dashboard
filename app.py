from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from src.merge_data import (
    build_merged_dataset,
    add_slope,
    add_volatility,
    add_fx_change,
)
from src.charts import (
    yields_chart,
    slope_chart,
    volatility_chart,
    usdjpy_chart,
    PLOTLY_CONFIG,
)
from src.theme import get_theme
from src.sparkline import sparkline_svg

SPARK_DAYS = 30
CHART_COLS = 2

st.set_page_config(page_title="JGB Bond Stress Dashboard", layout="wide")

if "theme_name" not in st.session_state:
    # Persist across a hard refresh via the URL, since st.session_state
    # resets on a new browser session but query params survive a reload.
    query_theme = st.query_params.get("theme")
    st.session_state.theme_name = query_theme if query_theme in ("light", "dark") else "dark"
    st.query_params["theme"] = st.session_state.theme_name

CSS_PATH = Path(__file__).parent / "assets" / "style.css"
theme = get_theme(st.session_state.theme_name)
st.markdown(f"<style>{CSS_PATH.read_text().format(**theme)}</style>", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = build_merged_dataset()
    df = add_slope(df)
    df = add_volatility(df)
    df = add_fx_change(df)
    return df


def status_color(value, thresholds=(0.3, 0.8)):
    if abs(value) < thresholds[0]:
        return theme["green"]
    if abs(value) < thresholds[1]:
        return theme["amber"]
    return theme["red"]


def kpi_card(label, value, delta, color, series):
    spark = sparkline_svg(series.tolist(), color)
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent:{color};">
            <div class="kpi-text">
                <p class="kpi-label">{label}</p>
                <p class="kpi-value" style="color:{color};">{value}</p>
                <p class="kpi-delta" style="color:{theme['muted']};">{delta}</p>
            </div>
            <div class="kpi-spark">{spark}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_panel(title, fig, accent, index):
    dot = f'<span class="legend-dot" style="background:{accent};"></span>' if accent else ""
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="panel-header-row">
                <p class="panel-title">{dot}{title}</p>
                <div class="chart-zoom-bar">
                    <button class="chart-zoom-btn" data-chart-index="{index}" data-action="out" title="Zoom out">&minus;</button>
                    <button class="chart-zoom-btn" data-chart-index="{index}" data-action="in" title="Zoom in">+</button>
                    <button class="chart-zoom-btn" data-chart-index="{index}" data-action="reset" title="Reset zoom">&#8635;</button>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key=f"chart_{title}")


def status_legend():
    items = [("Calm", theme["green"]), ("Elevated", theme["amber"]), ("Stress", theme["red"])]
    dots = "".join(
        f'<span><span class="legend-dot" style="background:{color};"></span>{label}</span>'
        for label, color in items
    )
    st.markdown(f'<div class="legend-row">{dots}</div>', unsafe_allow_html=True)


def render_chart_grid(panels):
    for i in range(0, len(panels), CHART_COLS):
        cols = st.columns(CHART_COLS)
        for col, (index, (title, fig, accent)) in zip(cols, list(enumerate(panels))[i:i + CHART_COLS]):
            with col:
                chart_panel(title, fig, accent, index)


def zoom_controls_script():
    # st.markdown injects HTML via innerHTML, and <script> tags inserted that
    # way never execute (per DOM spec). components.html renders a real iframe
    # document instead, where scripts run — so we reach into window.parent to
    # act on the actual page's Plotly charts.
    components.html(
        """
        <script>
        (function() {
            const doc = window.parent.document;
            const Plotly = window.parent.Plotly;
            if (window.parent.__zoomBarBound) return;
            window.parent.__zoomBarBound = true;

            function getRangeMs(gd) {
                const xr = gd.layout.xaxis.range;
                if (xr && xr.length === 2) {
                    return [new Date(xr[0]).getTime(), new Date(xr[1]).getTime()];
                }
                let allX = [];
                gd.data.forEach(tr => { allX = allX.concat(tr.x); });
                const times = allX.map(d => new Date(d).getTime());
                return [Math.min(...times), Math.max(...times)];
            }

            doc.addEventListener('click', function(e) {
                const btn = e.target.closest('.chart-zoom-btn');
                if (!btn) return;
                const plots = doc.querySelectorAll('.js-plotly-plot');
                const gd = plots[parseInt(btn.dataset.chartIndex, 10)];
                if (!gd) return;
                const action = btn.dataset.action;

                if (action === 'reset') {
                    Plotly.relayout(gd, {'xaxis.autorange': true});
                    return;
                }
                const [start, end] = getRangeMs(gd);
                const center = (start + end) / 2;
                const halfSpan = (end - start) / 2;
                const factor = action === 'in' ? 0.8 : 1.25;
                const newHalf = halfSpan * factor;
                const newStart = new Date(center - newHalf).toISOString().slice(0, 10);
                const newEnd = new Date(center + newHalf).toISOString().slice(0, 10);
                Plotly.relayout(gd, {'xaxis.range': [newStart, newEnd]});
            });
        })();
        </script>
        """,
        height=0,
    )


df = load_data()
latest = df.iloc[-1]
prev = df.iloc[-2]

header_col, toggle_col = st.columns([5, 1])
with header_col:
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <p class="app-title">JGB BOND STRESS MONITOR</p>
                <p class="app-sub">Japanese Government Bond &middot; 1Y / 10Y &middot; USD/JPY</p>
            </div>
            <div style="text-align:right;">
                <p class="app-sub">DATA WINDOW</p>
                <p class="app-sub" style="color:{theme['muted']};">{df.index.min().date()} &rarr; {df.index.max().date()}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with toggle_col:
    st.markdown("<div class='theme-toggle'>", unsafe_allow_html=True)
    is_light = st.toggle("Light mode", value=(st.session_state.theme_name == "light"))
    st.markdown("</div>", unsafe_allow_html=True)
    new_theme = "light" if is_light else "dark"
    if new_theme != st.session_state.theme_name:
        st.session_state.theme_name = new_theme
        st.query_params["theme"] = new_theme
        st.rerun()

status_legend()

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
        color=status_color(latest["vol_30d"] * 20),
        series=df["vol_30d"].tail(SPARK_DAYS),
    ),
    dict(
        label="USD/JPY Daily Chg (%)",
        value=f"{latest['usdjpy_change']:+.3f}",
        delta=f"USD/JPY {latest['USDJPY']:.2f}",
        color=status_color(latest["usdjpy_change"], thresholds=(0.5, 1.2)),
        series=df["USDJPY"].tail(SPARK_DAYS),
    ),
]

for col, kpi in zip(st.columns(len(kpis)), kpis):
    with col:
        kpi_card(**kpi)

st.write("")

panels = [
    ("RAW YIELDS: 1Y vs 10Y", yields_chart(df, theme), None),
    ("YIELD CURVE SLOPE (10Y − 1Y)", slope_chart(df, theme), kpis[0]["color"]),
    ("30-DAY ROLLING VOLATILITY", volatility_chart(df, theme), kpis[1]["color"]),
    ("USD/JPY", usdjpy_chart(df, theme), kpis[2]["color"]),
]
render_chart_grid(panels)
zoom_controls_script()

st.markdown(
    f"""
    <div class="app-footer">
        Data: Ministry of Finance Japan (JGB yields, data.mof.go.jp) &middot; USD/JPY via yfinance (JPY=X)
        &middot; Analysis window 2011&ndash;2026
    </div>
    """,
    unsafe_allow_html=True,
)
