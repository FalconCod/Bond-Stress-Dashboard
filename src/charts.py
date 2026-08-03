import plotly.graph_objects as go

RANGE_BUTTONS = [
    dict(count=1, label="1m", step="month", stepmode="backward"),
    dict(count=3, label="3m", step="month", stepmode="backward"),
    dict(count=6, label="6m", step="month", stepmode="backward"),
    dict(count=1, label="YTD", step="year", stepmode="todate"),
    dict(count=1, label="1y", step="year", stepmode="backward"),
    dict(count=5, label="5y", step="year", stepmode="backward"),
    dict(step="all", label="max"),
]

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": True}


def _base_layout(fig, theme, height=320):
    fig.update_layout(
        height=height,
        dragmode="pan",
        uirevision="constant",
        transition={"duration": 0},
        plot_bgcolor=theme["panel"],
        paper_bgcolor=theme["panel"],
        font=dict(color=theme["text"], family="IBM Plex Mono", size=11),
        margin=dict(t=10, b=10, l=45, r=15),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.1, xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=theme["text"], family="IBM Plex Mono", size=11),
        ),
        hovermode="x",
        hoverlabel=dict(bgcolor=theme["panel"], font=dict(family="IBM Plex Mono", size=11, color=theme["text"])),
        xaxis=dict(
            color=theme["text"],
            tickfont=dict(color=theme["text"], family="IBM Plex Mono", size=11),
            linecolor=theme["border"],
            tickcolor=theme["border"],
            gridcolor=theme["border"],
            zerolinecolor=theme["border"],
            showspikes=True,
            spikemode="across",
            spikesnap="hovered data",
            spikethickness=1,
            spikedash="dot",
            spikecolor=theme["cyan"],
            rangeselector=dict(
                buttons=RANGE_BUTTONS,
                bgcolor=theme["bg"],
                activecolor=theme["border"],
                bordercolor=theme["border"],
                borderwidth=1,
                font=dict(color=theme["text"], size=10),
                y=1.25,
            ),
        ),
        yaxis=dict(
            color=theme["text"],
            tickfont=dict(color=theme["text"], family="IBM Plex Mono", size=11),
            linecolor=theme["border"],
            tickcolor=theme["border"],
            gridcolor=theme["border"],
            zerolinecolor=theme["border"],
            showspikes=True,
            spikemode="toaxis",
            spikesnap="hovered data",
            spikethickness=1,
            spikedash="dot",
            spikecolor=theme["cyan"],
            fixedrange=True,
            autorange=True,
        ),
    )
    return fig


def yields_chart(df, theme, height=320):
    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=df.index, y=df["1Y"], name="1Y", line=dict(width=1.6, color=theme["blue"])))
    fig.add_trace(go.Scattergl(x=df.index, y=df["10Y"], name="10Y", line=dict(width=1.6, color=theme["amber"])))
    return _base_layout(fig, theme, height)


def single_series_chart(df, theme, column, name, color_key, height=320):
    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=df.index, y=df[column], name=name, line=dict(width=1.6, color=theme[color_key]), showlegend=False))
    return _base_layout(fig, theme, height)


def slope_chart(df, theme, height=320):
    return single_series_chart(df, theme, "slope_10y_1y", "slope", "cyan", height)


def volatility_chart(df, theme, height=320):
    return single_series_chart(df, theme, "vol_30d", "vol_30d", "red", height)


def usdjpy_chart(df, theme, height=320):
    return single_series_chart(df, theme, "USDJPY", "USD/JPY", "green", height)
