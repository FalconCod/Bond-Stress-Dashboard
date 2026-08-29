import streamlit as st

st.set_page_config(page_title="JGB Bond Stress Dashboard", layout="wide")

if "theme_name" not in st.session_state:
    # Persist across a hard refresh via the URL, since st.session_state
    # resets on a new browser session but query params survive a reload.
    query_theme = st.query_params.get("theme")
    st.session_state.theme_name = query_theme if query_theme in ("light", "dark") else "dark"
    st.query_params["theme"] = st.session_state.theme_name

pg = st.navigation([
    st.Page("pages/overview.py", title="Overview", default=True),
    st.Page("pages/yield_curve.py", title="Yield Curve"),
])
pg.run()
