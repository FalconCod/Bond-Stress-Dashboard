"""Streamlit rendering helpers for the dashboard. Keeps app.py to layout
orchestration only — all HTML/markup generation lives here."""

from pathlib import Path

import streamlit as st

from src.charts import PLOTLY_CONFIG
from src.sparkline import sparkline_svg

CHART_COLS = 2
CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"


def inject_css(theme):
    st.markdown(f"<style>{CSS_PATH.read_text().format(**theme)}</style>", unsafe_allow_html=True)


def status_color(theme, value, thresholds=(0.3, 0.8)):
    if abs(value) < thresholds[0]:
        return theme["green"]
    if abs(value) < thresholds[1]:
        return theme["amber"]
    return theme["red"]


def render_header(theme, data_start, data_end):
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
                    <p class="app-sub" style="color:{theme['muted']};">{data_start} &rarr; {data_end}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with toggle_col:
        st.markdown("<div class='theme-toggle'>", unsafe_allow_html=True)
        is_light = st.toggle("Light mode", value=(st.session_state.theme_name == "light"))
        st.markdown("</div>", unsafe_allow_html=True)
        return "light" if is_light else "dark"


def render_status_legend(theme):
    items = [("Calm", theme["green"]), ("Elevated", theme["amber"]), ("Stress", theme["red"])]
    dots = "".join(
        f'<span><span class="legend-dot" style="background:{color};"></span>{label}</span>'
        for label, color in items
    )
    st.markdown(f'<div class="legend-row">{dots}</div>', unsafe_allow_html=True)


def render_kpi_card(theme, label, value, delta, color, series):
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


def render_kpi_row(theme, kpis):
    for col, kpi in zip(st.columns(len(kpis)), kpis):
        with col:
            render_kpi_card(theme, **kpi)


def render_chart_panel(title, fig, accent):
    dot = f'<span class="legend-dot" style="background:{accent};"></span>' if accent else ""
    with st.container(border=True):
        st.markdown(f"<p class='panel-title'>{dot}{title}</p>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key=f"chart_{title}")


def render_chart_grid(panels):
    for i in range(0, len(panels), CHART_COLS):
        cols = st.columns(CHART_COLS)
        for col, (title, fig, accent) in zip(cols, panels[i:i + CHART_COLS]):
            with col:
                render_chart_panel(title, fig, accent)


def render_footer():
    st.markdown(
        """
        <div class="app-footer">
            Data: Ministry of Finance Japan (JGB yields, data.mof.go.jp) &middot; USD/JPY via yfinance (JPY=X)
            &middot; Analysis window 2011&ndash;2026
        </div>
        """,
        unsafe_allow_html=True,
    )
