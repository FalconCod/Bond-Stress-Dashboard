"""Dashboard CSS, as a Python string rather than an assets/style.css file.

This is a *template* (string.Template $variables get substituted with the
active theme's colors at render time), not standalone CSS on its own — a
.css file with that content trips every editor's CSS linter, since $var
isn't valid CSS syntax. Living in a .py file sidesteps that entirely: no
language server tries to validate it as CSS.
"""

CSS_TEMPLATE = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace !important;
}

.stApp {
    background-color: $bg;
    color: $text;
}

section[data-testid="stSidebar"] {
    background-color: $panel;
    border-right: 1px solid $border;
}

[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebarNavLink"] p {
    color: $text !important;
}

[data-testid="stSidebarNavLink"][aria-current="page"] {
    background-color: $bg !important;
    color: $cyan !important;
}

[data-testid="stSidebarNavLink"][aria-current="page"] span,
[data-testid="stSidebarNavLink"][aria-current="page"] p {
    color: $cyan !important;
    font-weight: 600;
}

#MainMenu, footer {
    visibility: hidden;
}

/* The "reopen sidebar" button (stExpandSidebarButton) renders INSIDE
   this same header element, not as a separate one -- so the header
   itself must stay visible and interactive, or a collapsed sidebar can
   never be reopened. Blend it into the theme instead of hiding it. */
header[data-testid="stHeader"] {
    background-color: $bg;
}

/* The expand/collapse icons default to Streamlit's own theme color,
   which assumes a dark header -- invisible against our light-theme
   background. These are NOT <svg> icons: Streamlit renders them as a
   `stIconMaterial` span (Material Symbols font glyph) with `color`
   passed in as a prop, which becomes an inline style -- an ancestor
   `color` rule can't override a descendant's own explicit value, only
   `!important` on that exact element can. */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] {
    color: $text !important;
}

[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
    color: $text !important;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: $panel;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: $border !important;
}

.app-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 1px solid $border;
    padding-bottom: 10px;
    margin-bottom: 18px;
}

.app-title {
    font-size: 20px;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: $text;
    margin: 0;
}

.app-sub {
    font-size: 12px;
    color: $muted;
    margin: 0;
}

.kpi-card {
    background-color: $panel;
    border: 1px solid $border;
    border-left: 3px solid var(--accent, $border);
    box-sizing: border-box;
    padding: 12px 16px;
    min-height: 90px;
    overflow: hidden;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
}

.kpi-text {
    min-width: 0;
    flex: 1;
}

.kpi-label {
    font-size: 11px;
    color: $muted;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin: 0 0 6px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.kpi-value {
    font-size: 22px;
    font-weight: 600;
    margin: 0;
    line-height: 1.3;
}

.kpi-delta {
    font-size: 11px;
    margin: 4px 0 0 0;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.kpi-spark {
    flex-shrink: 0;
    margin-top: 4px;
}

.panel-title {
    font-size: 12px;
    color: $muted;
    letter-spacing: 0.6px;
    margin: 0 0 4px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Sidebar toggle label text ("Light mode") -- stWidgetLabel is Streamlit's
   generic wrapper for every widget's label, scoped to the sidebar here
   so it doesn't recolor widget labels added elsewhere later. */
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: $text !important;
}

.legend-row {
    display: flex;
    gap: 20px;
    align-items: center;
    margin: 10px 0 18px 0;
    font-size: 11px;
    color: $muted;
}

.legend-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

.app-footer {
    margin-top: 24px;
    padding-top: 12px;
    border-top: 1px solid $border;
    font-size: 11px;
    color: $muted;
}
"""
