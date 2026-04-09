"""
Reusable Plotly chart components for the dashboard.
Premium midnight theme with cyan/violet accent palette.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ─── Premium Color Palette ────────────────────────────────────
BRAND_COLORS = {
    "Safari":             "#34d399",   # emerald
    "Skybags":            "#38bdf8",   # sky blue
    "American Tourister": "#fbbf24",   # amber gold
    "VIP":                "#f87171",   # rose
    "Aristocrat":         "#a78bfa",   # violet
    "Nasher Miles":       "#fb7185",   # pink
}

GRADIENT_COLORS = ["#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#fb7185", "#38bdf8"]

SENTIMENT_COLORS = {
    "Positive": "#34d399",
    "Neutral":  "#fbbf24",
    "Negative": "#f87171",
}

# Plotly layout defaults — dark transparent
CHART_BG = "rgba(0,0,0,0)"
CHART_FONT = dict(family="Outfit, sans-serif", size=12, color="#94a3b8")
CHART_MARGINS = dict(l=48, r=32, t=52, b=44)
GRID_COLOR = "rgba(255,255,255,0.04)"
AXIS_COLOR = "rgba(255,255,255,0.08)"


def apply_chart_style(fig, height=400):
    """Apply the premium midnight-glass style to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        font=CHART_FONT,
        height=height,
        margin=CHART_MARGINS,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.06)",
            borderwidth=1,
            font=dict(size=11, color="#94a3b8"),
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=AXIS_COLOR,
            tickfont=dict(color="#64748b"),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=AXIS_COLOR,
            tickfont=dict(color="#64748b"),
        ),
    )
    return fig


def create_brand_bar_chart(data, x, y, title="", color_col=None, orientation="v"):
    """Create a branded bar chart with glow effect."""
    if color_col:
        colors = [BRAND_COLORS.get(b, "#22d3ee") for b in data[color_col]]
    else:
        colors = [BRAND_COLORS.get(b, "#22d3ee") for b in data[x]]

    if orientation == "v":
        fig = go.Figure(go.Bar(
            x=data[x], y=data[y],
            marker_color=colors,
            marker_line_width=0,
            marker_opacity=0.9,
            text=data[y].round(2) if data[y].dtype in ['float64', 'float32'] else data[y],
            textposition="outside",
            textfont=dict(size=11, family="Outfit", color="#e2e8f0"),
        ))
    else:
        fig = go.Figure(go.Bar(
            y=data[x], x=data[y],
            marker_color=colors,
            marker_line_width=0,
            marker_opacity=0.9,
            orientation='h',
            text=data[y].round(2) if data[y].dtype in ['float64', 'float32'] else data[y],
            textposition="outside",
            textfont=dict(size=11, family="Outfit", color="#e2e8f0"),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#f1f5f9")),
    )
    return apply_chart_style(fig)


def create_radar_chart(brands_data, categories, title="Brand Comparison Radar"):
    """Create a radar chart with translucent fills."""
    fig = go.Figure()

    for brand, values in brands_data.items():
        values_closed = values + [values[0]]
        cats_closed = categories + [categories[0]]
        hex_color = BRAND_COLORS.get(brand, "#22d3ee")
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)

        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=cats_closed,
            name=brand,
            fill='toself',
            fillcolor=f"rgba({r},{g},{b},0.08)",
            line=dict(color=hex_color, width=2),
            marker=dict(size=4, color=hex_color),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#f1f5f9")),
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                showticklabels=True, tickfont=dict(size=9, color="#475569"),
                gridcolor="rgba(255,255,255,0.04)",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#94a3b8"),
                gridcolor="rgba(255,255,255,0.04)",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
    )
    return apply_chart_style(fig, height=460)


def create_price_distribution(products_df, title="Price Distribution by Brand"):
    """Create a premium box plot."""
    fig = go.Figure()

    for brand in sorted(products_df["brand"].unique()):
        brand_data = products_df[products_df["brand"] == brand]
        fig.add_trace(go.Box(
            y=brand_data["price"],
            name=brand,
            marker_color=BRAND_COLORS.get(brand, "#22d3ee"),
            line_color=BRAND_COLORS.get(brand, "#22d3ee"),
            fillcolor=f"rgba({int(BRAND_COLORS.get(brand,'#22d3ee')[1:3],16)},{int(BRAND_COLORS.get(brand,'#22d3ee')[3:5],16)},{int(BRAND_COLORS.get(brand,'#22d3ee')[5:7],16)},0.15)",
            boxmean=True,
            jitter=0.3,
            pointpos=-1.5,
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#f1f5f9")),
        yaxis_title="Price (₹)",
        showlegend=False,
    )
    return apply_chart_style(fig, height=400)


def create_sentiment_gauge(score, title="Sentiment Score", max_val=1.0):
    """Create a sleek gauge chart."""
    if score > 0.3:
        color = "#34d399"
    elif score > 0:
        color = "#fbbf24"
    else:
        color = "#f87171"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score, 3),
        title=dict(text=title, font=dict(size=13, color="#94a3b8", family="Outfit")),
        number=dict(font=dict(size=28, color="#f1f5f9", family="Outfit"), valueformat="+.3f"),
        gauge=dict(
            axis=dict(range=[-max_val, max_val], tickwidth=1, dtick=0.25,
                      tickcolor="#334155", tickfont=dict(color="#475569")),
            bar=dict(color=color, thickness=0.65),
            bgcolor="rgba(255,255,255,0.02)",
            borderwidth=1,
            bordercolor="rgba(255,255,255,0.06)",
            steps=[
                dict(range=[-max_val, -0.15], color="rgba(248,113,113,0.06)"),
                dict(range=[-0.15, 0.15], color="rgba(251,191,36,0.06)"),
                dict(range=[0.15, max_val], color="rgba(52,211,153,0.06)"),
            ],
        ),
    ))
    return apply_chart_style(fig, height=250)


def create_aspect_heatmap(matrix_df, title="Aspect Sentiment Heatmap"):
    """Create a heatmap for brand × aspect sentiments."""
    fig = go.Figure(go.Heatmap(
        z=matrix_df.values,
        x=matrix_df.columns.tolist(),
        y=matrix_df.index.tolist(),
        colorscale=[
            [0.0, "#991b1b"],
            [0.25, "#f87171"],
            [0.45, "#fbbf24"],
            [0.55, "#fde68a"],
            [0.75, "#6ee7b7"],
            [1.0, "#059669"],
        ],
        zmid=0,
        text=np.round(matrix_df.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=11, color="#e2e8f0"),
        hovertemplate="Brand: %{y}<br>Aspect: %{x}<br>Sentiment: %{z:.3f}<extra></extra>",
        colorbar=dict(
            title=dict(text="Sentiment", font=dict(size=11, color="#94a3b8")),
            tickformat="+.2f",
            tickfont=dict(color="#64748b"),
        ),
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#f1f5f9")),
        xaxis=dict(tickangle=45, tickfont=dict(color="#94a3b8")),
        yaxis=dict(tickfont=dict(color="#94a3b8")),
    )
    return apply_chart_style(fig, height=380)


def create_scatter_plot(df, x, y, color_col, size_col=None, title=""):
    """Create a scatter plot with brand-colored markers."""
    fig = go.Figure()

    for brand in df[color_col].unique():
        bd = df[df[color_col] == brand]
        marker_size = bd[size_col] if size_col and size_col in bd.columns else 12
        fig.add_trace(go.Scatter(
            x=bd[x], y=bd[y],
            mode="markers",
            name=brand,
            marker=dict(
                color=BRAND_COLORS.get(brand, "#22d3ee"),
                size=marker_size,
                sizemode="area",
                sizeref=2. * max(df[size_col].max() if size_col and size_col in df.columns else 12, 1) / (30.**2),
                sizemin=6,
                line=dict(width=1.5, color="rgba(0,0,0,0.3)"),
                opacity=0.85,
            ),
            text=bd["title"] if "title" in bd.columns else None,
            hovertemplate=f"<b>{brand}</b><br>{x}: %{{x}}<br>{y}: %{{y}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#f1f5f9")),
        xaxis_title=x.replace("_", " ").title(),
        yaxis_title=y.replace("_", " ").title(),
    )
    return apply_chart_style(fig, height=420)


def create_pie_chart(labels, values, title="", colors=None):
    """Create a donut chart with premium styling."""
    if colors is None:
        colors = [SENTIMENT_COLORS.get(l, "#22d3ee") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(
            colors=colors,
            line=dict(color="rgba(3,7,18,0.8)", width=3),
        ),
        hole=0.5,
        textinfo="label+percent",
        textfont=dict(size=12, color="#e2e8f0", family="Outfit"),
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
        pull=[0.02] * len(labels),
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#f1f5f9")),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.18,
            font=dict(color="#94a3b8"),
        ),
    )
    return apply_chart_style(fig, height=350)


def create_grouped_bar(df, x, y_cols, title="", y_names=None):
    """Create a grouped bar chart."""
    fig = go.Figure()
    colors = GRADIENT_COLORS[:len(y_cols)]

    for i, col in enumerate(y_cols):
        name = y_names[i] if y_names else col.replace("_", " ").title()
        fig.add_trace(go.Bar(
            x=df[x], y=df[col],
            name=name,
            marker_color=colors[i],
            marker_opacity=0.9,
            text=df[col].round(2) if df[col].dtype in ['float64', 'float32'] else df[col],
            textposition="outside",
            textfont=dict(size=10, color="#94a3b8"),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#f1f5f9")),
        barmode="group",
        xaxis_tickangle=-30,
    )
    return apply_chart_style(fig, height=420)


def create_trust_gauge(score, title="Trust Score"):
    """Create a trust score gauge (0-100 scale)."""
    if score >= 70:
        color = "#34d399"
    elif score >= 50:
        color = "#fbbf24"
    else:
        color = "#f87171"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title=dict(text=title, font=dict(size=12, color="#94a3b8", family="Outfit")),
        number=dict(font=dict(size=24, color="#f1f5f9", family="Outfit"), suffix="/100"),
        gauge=dict(
            axis=dict(range=[0, 100], dtick=25,
                      tickcolor="#334155", tickfont=dict(color="#475569")),
            bar=dict(color=color, thickness=0.65),
            bgcolor="rgba(255,255,255,0.02)",
            borderwidth=1,
            bordercolor="rgba(255,255,255,0.06)",
            steps=[
                dict(range=[0, 50], color="rgba(248,113,113,0.04)"),
                dict(range=[50, 70], color="rgba(251,191,36,0.04)"),
                dict(range=[70, 100], color="rgba(52,211,153,0.04)"),
            ],
        ),
    ))
    return apply_chart_style(fig, height=220)
