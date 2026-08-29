"""Streamlit rendering helpers for the dashboard. Keeps app.py to layout
orchestration only — all HTML/markup generation lives here."""

from string import Template

import streamlit as st

from src.charts import PLOTLY_CONFIG
from src.sparkline import sparkline_svg
from src.styles import CSS_TEMPLATE

CHART_COLS = 2


def inject_css(theme):
    css = Template(CSS_TEMPLATE).substitute(**theme)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def status_color(theme, value, thresholds=(0.3, 0.8)):
    if abs(value) < thresholds[0]:
        return theme["green"]
    if abs(value) < thresholds[1]:
        return theme["amber"]
    return theme["red"]


def render_theme_toggle_sidebar(theme):
    """Theme toggle lives in the sidebar rather than a per-page header, so
    it's in the same place and behaves identically on every page of the
    multi-page app. Styled via the sidebar-scoped stWidgetLabel selector
    in style.css, not a wrapper div — st.markdown calls each render into
    their own container, so an opening tag from one call and a closing
    tag from another never actually nest anything in the real DOM."""
    with st.sidebar:
        is_light = st.toggle("Light mode", value=(st.session_state.theme_name == "light"))
    return "light" if is_light else "dark"


def render_page_header(theme, title, subtitle, data_start=None, data_end=None):
    # Built as flat, unindented strings rather than nested triple-quoted
    # blocks: splicing an indented f-string into another indented
    # f-string pushes some lines past 4 leading spaces, which CommonMark
    # reads as an indented code block and renders as literal text
    # instead of parsing as HTML.
    date_html = ""
    if data_start is not None and data_end is not None:
        date_html = (
            '<div style="text-align:right;">'
            '<p class="app-sub">DATA WINDOW</p>'
            f'<p class="app-sub" style="color:{theme["muted"]};">{data_start} &rarr; {data_end}</p>'
            "</div>"
        )
    header_html = (
        '<div class="app-header">'
        "<div>"
        f'<p class="app-title">{title}</p>'
        f'<p class="app-sub">{subtitle}</p>'
        "</div>"
        f"{date_html}"
        "</div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)


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
        st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, key=f"chart_{title}")


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
