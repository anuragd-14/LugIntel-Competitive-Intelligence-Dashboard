"""
Dashboard Overview Page
========================
Provides a high-level summary of the competitive intelligence analysis:
- Hero KPI cards (brands, products, reviews, avg sentiment, pricing)
- Price distribution by brand (box plot)
- Sentiment snapshot per brand (bar + gauge)
- Quick brand ranking table (sortable)
"""

import streamlit as st
import pandas as pd
import numpy as np
from dashboard.components.charts import (
    create_brand_bar_chart, create_price_distribution,
    create_sentiment_gauge, create_pie_chart, create_scatter_plot,
    BRAND_COLORS, apply_chart_style
)
import plotly.graph_objects as go


def render_overview(products, reviews, brand_sentiment, themes):
    """Render the Dashboard Overview page."""

    # ─── Header ──────────────────────────────────────────────
    st.markdown("# 📊 Dashboard Overview")
    st.markdown(
        "High-level snapshot of competitive intelligence across **6 luggage brands** "
        "on Amazon India. Covering pricing, sentiment, and market positioning."
    )
    st.divider()

    # ─── Hero KPI Cards ──────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.metric("🏷️ Brands Tracked", len(products["brand"].unique()))
    with k2:
        st.metric("📦 Total Products", len(products))
    with k3:
        st.metric("💬 Total Reviews", f"{len(reviews):,}")
    with k4:
        avg_price = products["price"].mean()
        st.metric("💰 Avg Price", f"₹{avg_price:,.0f}")
    with k5:
        if brand_sentiment is not None:
            avg_sent = brand_sentiment["avg_sentiment"].mean()
            st.metric("😊 Avg Sentiment", f"{avg_sent:+.3f}")
        else:
            st.metric("⭐ Avg Rating", f"{products['rating'].mean():.1f}")

    st.divider()

    # ─── Row 1: Price & Rating Overview ──────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💰 Price Distribution by Brand")
        fig = create_price_distribution(products)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### ⭐ Average Rating by Brand")
        brand_ratings = products.groupby("brand")["rating"].mean().reset_index()
        brand_ratings = brand_ratings.sort_values("rating", ascending=False)
        fig = create_brand_bar_chart(brand_ratings, "brand", "rating",
                                     title="")
        fig.update_layout(yaxis_range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)

    # ─── Row 2: Sentiment Overview ───────────────────────────
    st.divider()
    st.markdown("### 😊 Sentiment Analysis Snapshot")

    if brand_sentiment is not None:
        # Sentiment bar chart
        col1, col2 = st.columns([3, 2])

        with col1:
            bs = brand_sentiment.reset_index()
            bs = bs.sort_values("avg_sentiment", ascending=True)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=bs["brand"],
                x=bs["avg_sentiment"],
                orientation='h',
                marker_color=[BRAND_COLORS.get(b, "#22d3ee") for b in bs["brand"]],
                marker_opacity=0.9,
                text=bs["avg_sentiment"].round(3).apply(lambda x: f"+{x:.3f}" if x > 0 else f"{x:.3f}"),
                textposition="outside",
                textfont=dict(size=12, family="Outfit", color="#e2e8f0"),
            ))
            fig.update_layout(
                title=dict(text="Average Sentiment Score by Brand", font=dict(size=15, color="#f1f5f9")),
                xaxis_title="Combined Sentiment Score",
                xaxis_range=[-0.2, 1.0],
                height=350,
                margin=dict(l=130, r=60, t=50, b=40),
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Outfit, sans-serif", color="#94a3b8"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Sentiment distribution pie
            if "sentiment_label" in reviews.columns:
                sent_counts = reviews["sentiment_label"].value_counts()
                fig = create_pie_chart(
                    sent_counts.index.tolist(),
                    sent_counts.values.tolist(),
                    title="Overall Sentiment Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)

        # Sentiment percentage breakdown per brand
        st.markdown("#### Sentiment Breakdown by Brand")
        
        if "sentiment_label" in reviews.columns:
            brand_sent_pct = reviews.groupby("brand")["sentiment_label"].value_counts(normalize=True).unstack(fill_value=0) * 100
            
            fig = go.Figure()
            colors = {"Positive": "#34d399", "Neutral": "#fbbf24", "Negative": "#f87171"}
            for label in ["Positive", "Neutral", "Negative"]:
                if label in brand_sent_pct.columns:
                    fig.add_trace(go.Bar(
                        x=brand_sent_pct.index,
                        y=brand_sent_pct[label],
                        name=label,
                        marker_color=colors[label],
                        marker_opacity=0.88,
                        text=brand_sent_pct[label].round(1).apply(lambda x: f"{x:.0f}%"),
                        textposition="inside",
                        textfont=dict(color="#030712", size=11),
                    ))
            
            fig.update_layout(
                barmode="stack",
                title=dict(text="Sentiment Distribution (%) per Brand", font=dict(size=15, color="#f1f5f9")),
                yaxis_title="Percentage",
                height=380,
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Outfit, sans-serif", color="#94a3b8"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color="#94a3b8")),
            )
            st.plotly_chart(fig, use_container_width=True)

    # ─── Row 3: Pricing & Discount Analysis ──────────────────
    st.divider()
    st.markdown("### 🏷️ Pricing & Discount Analysis")

    col1, col2 = st.columns(2)

    with col1:
        brand_pricing = products.groupby("brand").agg(
            avg_price=("price", "mean"),
            avg_list_price=("list_price", "mean"),
        ).reset_index().sort_values("avg_price", ascending=False)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=brand_pricing["brand"],
            y=brand_pricing["avg_list_price"],
            name="List Price (MRP)",
            marker_color="rgba(34,211,238,0.15)",
            text=brand_pricing["avg_list_price"].round(0).apply(lambda x: f"₹{x:,.0f}"),
            textposition="outside",
            textfont=dict(size=10, color="#64748b"),
        ))
        fig.add_trace(go.Bar(
            x=brand_pricing["brand"],
            y=brand_pricing["avg_price"],
            name="Selling Price",
            marker_color=[BRAND_COLORS.get(b, "#22d3ee") for b in brand_pricing["brand"]],
            marker_opacity=0.9,
            text=brand_pricing["avg_price"].round(0).apply(lambda x: f"₹{x:,.0f}"),
            textposition="outside",
            textfont=dict(size=10, color="#e2e8f0"),
        ))
        fig.update_layout(
            title=dict(text="Average MRP vs Selling Price", font=dict(size=15, color="#f1f5f9")),
            barmode="group",
            yaxis_title="Price (₹)",
            height=400,
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Outfit, sans-serif", color="#94a3b8"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        brand_disc = products.groupby("brand")["discount_pct"].mean().reset_index()
        brand_disc = brand_disc.sort_values("discount_pct", ascending=False)

        fig = create_brand_bar_chart(
            brand_disc, "brand", "discount_pct",
            title="Average Discount % by Brand"
        )
        fig.update_layout(yaxis_title="Discount (%)")
        fig.update_traces(text=brand_disc["discount_pct"].round(1).apply(lambda x: f"{x:.1f}%"))
        st.plotly_chart(fig, use_container_width=True)

    # ─── Row 4: Brand Ranking Table ──────────────────────────
    st.divider()
    st.markdown("### 🏆 Brand Ranking Table")
    st.markdown("*Click column headers to sort*")

    brand_table = products.groupby("brand").agg(
        products_count=("product_id", "count"),
        avg_price=("price", "mean"),
        avg_discount=("discount_pct", "mean"),
        avg_rating=("rating", "mean"),
        total_reviews=("review_count", "sum"),
    ).reset_index()

    if brand_sentiment is not None:
        bs = brand_sentiment.reset_index()[["brand", "avg_sentiment", "positive_pct", "negative_pct"]]
        brand_table = brand_table.merge(bs, on="brand", how="left")

    # Format
    brand_table["avg_price"] = brand_table["avg_price"].round(0).apply(lambda x: f"₹{x:,.0f}")
    brand_table["avg_discount"] = brand_table["avg_discount"].round(1).apply(lambda x: f"{x}%")
    brand_table["avg_rating"] = brand_table["avg_rating"].round(2).apply(lambda x: f"{x} ⭐")
    brand_table["total_reviews"] = brand_table["total_reviews"].apply(lambda x: f"{x:,}")

    if "avg_sentiment" in brand_table.columns:
        brand_table["avg_sentiment"] = brand_table["avg_sentiment"].round(3).apply(
            lambda x: f"+{x:.3f}" if x > 0 else f"{x:.3f}"
        )
        brand_table["positive_pct"] = brand_table["positive_pct"].round(0).apply(lambda x: f"{x:.0f}%")
        brand_table["negative_pct"] = brand_table["negative_pct"].round(0).apply(lambda x: f"{x:.0f}%")

    display_cols = {
        "brand": "Brand",
        "products_count": "Products",
        "avg_price": "Avg Price",
        "avg_discount": "Avg Discount",
        "avg_rating": "Rating",
        "total_reviews": "Reviews",
    }
    if "avg_sentiment" in brand_table.columns:
        display_cols["avg_sentiment"] = "Sentiment"
        display_cols["positive_pct"] = "Positive %"
        display_cols["negative_pct"] = "Negative %"

    display_df = brand_table[list(display_cols.keys())].rename(columns=display_cols)
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=280)

    # ─── Row 5: Key Themes ───────────────────────────────────
    if themes:
        st.divider()
        st.markdown("### 💬 Key Review Themes by Brand")

        cols = st.columns(3)
        for i, (brand, theme_data) in enumerate(themes.items()):
            with cols[i % 3]:
                st.markdown(f"**{brand}**")
                
                pos = theme_data.get("positive_themes", [])[:4]
                neg = theme_data.get("negative_themes", [])[:4]
                
                if pos:
                    st.markdown("✅ **Praise:**")
                    for p in pos:
                        kw = p["keyword"] if isinstance(p, dict) else p
                        st.markdown(f"  - {kw}")
                
                if neg:
                    st.markdown("❌ **Complaints:**")
                    for n in neg:
                        kw = n["keyword"] if isinstance(n, dict) else n
                        st.markdown(f"  - {kw}")
                
                st.markdown("---")
