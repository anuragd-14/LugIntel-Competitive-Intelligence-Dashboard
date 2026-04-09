"""
Brand Comparison Page
======================
Side-by-side comparison of selected brands on all key metrics:
- Radar chart for multi-dimensional comparison
- Bar charts for price, discount, rating, sentiment
- Aspect sentiment heatmap (BONUS)
- Detailed comparison table (sortable)
- Top pros/cons per brand
"""

import streamlit as st
import pandas as pd
import numpy as np
from dashboard.components.charts import (
    create_radar_chart, create_brand_bar_chart, create_aspect_heatmap,
    create_grouped_bar, create_scatter_plot, create_pie_chart,
    BRAND_COLORS, apply_chart_style
)
from dashboard.components.filters import render_brand_filter, render_price_filter
import plotly.graph_objects as go


def render_brand_comparison(products, reviews, brand_sentiment, themes,
                           aspect_matrix, aspect_sentiments, vfm_data, price_bands):
    """Render the Brand Comparison page."""

    # ─── Header ──────────────────────────────────────────────
    st.markdown("# ⚔️ Brand Comparison")
    st.markdown(
        "Compare luggage brands head-to-head across pricing, sentiment, "
        "quality, and value-for-money metrics."
    )
    st.divider()

    # ─── Brand Selector ──────────────────────────────────────
    all_brands = sorted(products["brand"].unique().tolist())
    selected_brands = st.multiselect(
        "🏷️ Select brands to compare",
        options=all_brands,
        default=all_brands,
        key="comparison_brands",
    )

    if not selected_brands:
        st.warning("Please select at least one brand to compare.")
        return

    # Filter data
    fp = products[products["brand"].isin(selected_brands)]
    fr = reviews[reviews["brand"].isin(selected_brands)] if reviews is not None else None

    # ─── Radar Chart ─────────────────────────────────────────
    st.divider()
    st.markdown("### 🎯 Multi-Dimensional Brand Comparison")

    # Build radar data
    brand_stats = {}
    for brand in selected_brands:
        bp = fp[fp["brand"] == brand]
        br = fr[fr["brand"] == brand] if fr is not None else pd.DataFrame()
        
        # Normalize to 0-100 scale
        avg_price = bp["price"].mean()
        price_comp = max(0, 100 - (avg_price / fp["price"].max()) * 100)  # Lower price = higher score
        
        avg_rating = bp["rating"].mean()
        rating_score = (avg_rating / 5.0) * 100
        
        avg_discount = bp["discount_pct"].mean()
        discount_score = min(100, avg_discount * 3)  # Scale up
        
        review_count = bp["review_count"].sum()
        review_score = min(100, (review_count / max(fp.groupby("brand")["review_count"].sum().max(), 1)) * 100)
        
        sentiment_score = 50  # default
        if brand_sentiment is not None and brand in brand_sentiment.index:
            raw_sent = brand_sentiment.loc[brand, "avg_sentiment"]
            sentiment_score = min(100, max(0, (raw_sent + 1) / 2 * 100))
        
        brand_stats[brand] = [
            round(rating_score, 1),
            round(sentiment_score, 1),
            round(price_comp, 1),
            round(review_score, 1),
            round(discount_score, 1),
        ]

    categories = ["Rating", "Sentiment", "Price Value", "Popularity", "Discount Depth"]
    fig = create_radar_chart(brand_stats, categories, title="")
    st.plotly_chart(fig, use_container_width=True)

    # ─── Key Metrics Comparison ──────────────────────────────
    st.divider()
    st.markdown("### 📊 Key Metrics Comparison")

    col1, col2 = st.columns(2)

    with col1:
        # Average Price
        brand_prices = fp.groupby("brand")["price"].mean().reset_index()
        brand_prices = brand_prices.sort_values("price", ascending=False)
        fig = create_brand_bar_chart(brand_prices, "brand", "price", title="Average Selling Price (₹)")
        fig.update_layout(yaxis_title="Price (₹)")
        fig.update_traces(text=brand_prices["price"].round(0).apply(lambda x: f"₹{x:,.0f}"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Average Rating
        brand_ratings = fp.groupby("brand")["rating"].mean().reset_index()
        brand_ratings = brand_ratings.sort_values("rating", ascending=False)
        fig = create_brand_bar_chart(brand_ratings, "brand", "rating", title="Average Star Rating")
        fig.update_layout(yaxis_range=[0, 5], yaxis_title="Rating (0-5)")
        fig.update_traces(text=brand_ratings["rating"].round(2).apply(lambda x: f"{x:.2f} ⭐"))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # Average Discount
        brand_disc = fp.groupby("brand")["discount_pct"].mean().reset_index()
        brand_disc = brand_disc.sort_values("discount_pct", ascending=False)
        fig = create_brand_bar_chart(brand_disc, "brand", "discount_pct", title="Average Discount %")
        fig.update_layout(yaxis_title="Discount (%)")
        fig.update_traces(text=brand_disc["discount_pct"].round(1).apply(lambda x: f"{x:.1f}%"))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        # Sentiment Score
        if brand_sentiment is not None:
            bs = brand_sentiment.reset_index()
            bs = bs[bs["brand"].isin(selected_brands)]
            bs = bs.sort_values("avg_sentiment", ascending=False)
            fig = create_brand_bar_chart(bs, "brand", "avg_sentiment", title="Average Sentiment Score")
            fig.update_layout(yaxis_title="Sentiment (-1 to +1)")
            fig.update_traces(text=bs["avg_sentiment"].round(3).apply(
                lambda x: f"+{x:.3f}" if x > 0 else f"{x:.3f}"
            ))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sentiment data not available.")

    # ─── Price vs Sentiment Scatter ──────────────────────────
    st.divider()
    st.markdown("### 💡 Price vs Sentiment Analysis")
    st.markdown("*Bubble size = number of reviews. Ideally you want to be in the top-left (low price, high sentiment).*")

    if "combined_score" in fr.columns:
        prod_sent = fr.groupby("product_id")["combined_score"].mean().reset_index()
        prod_sent.columns = ["product_id", "avg_sentiment"]
        scatter_df = fp.merge(prod_sent, on="product_id", how="left")
        scatter_df["avg_sentiment"] = scatter_df["avg_sentiment"].fillna(0)

        fig = create_scatter_plot(
            scatter_df, "price", "avg_sentiment", "brand",
            size_col="review_count",
            title="Price vs Customer Sentiment (Bubble = Review Count)"
        )
        fig.update_layout(
            xaxis_title="Selling Price (₹)",
            yaxis_title="Average Sentiment Score",
        )
        # Add quadrant lines
        fig.add_hline(y=scatter_df["avg_sentiment"].median(), line_dash="dash",
                     line_color="rgba(34,211,238,0.2)")
        fig.add_vline(x=scatter_df["price"].median(), line_dash="dash",
                     line_color="rgba(34,211,238,0.2)")
        st.plotly_chart(fig, use_container_width=True)

    # ─── Aspect Sentiment Heatmap (BONUS) ────────────────────
    if aspect_matrix is not None:
        st.divider()
        st.markdown("### 🔬 Aspect-Level Sentiment Heatmap")
        st.markdown(
            "*How each brand performs on specific luggage attributes. "
            "Green = positive, Red = negative.*"
        )

        filtered_matrix = aspect_matrix.loc[
            aspect_matrix.index.isin(selected_brands)
        ]
        if not filtered_matrix.empty:
            fig = create_aspect_heatmap(filtered_matrix, title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No aspect data available for selected brands.")

    # ─── Detailed Comparison Table ───────────────────────────
    st.divider()
    st.markdown("### 📋 Detailed Comparison Table")

    comp_data = []
    for brand in selected_brands:
        bp = fp[fp["brand"] == brand]
        br = fr[fr["brand"] == brand] if fr is not None else pd.DataFrame()

        row = {
            "Brand": brand,
            "Products": len(bp),
            "Avg Price": f"₹{bp['price'].mean():,.0f}",
            "Price Range": f"₹{bp['price'].min():,.0f} - ₹{bp['price'].max():,.0f}",
            "Avg Discount": f"{bp['discount_pct'].mean():.1f}%",
            "Avg Rating": f"{bp['rating'].mean():.2f} ⭐",
            "Total Reviews": f"{bp['review_count'].sum():,}",
        }

        if brand_sentiment is not None and brand in brand_sentiment.index:
            row["Sentiment"] = f"+{brand_sentiment.loc[brand, 'avg_sentiment']:.3f}" \
                if brand_sentiment.loc[brand, "avg_sentiment"] > 0 \
                else f"{brand_sentiment.loc[brand, 'avg_sentiment']:.3f}"
            row["Positive %"] = f"{brand_sentiment.loc[brand, 'positive_pct']:.0f}%"
            row["Negative %"] = f"{brand_sentiment.loc[brand, 'negative_pct']:.0f}%"

        comp_data.append(row)

    comp_df = pd.DataFrame(comp_data)
    st.dataframe(comp_df, use_container_width=True, hide_index=True, height=280)

    # ─── Top Pros and Cons ───────────────────────────────────
    if themes:
        st.divider()
        st.markdown("### 👍👎 Top Pros & Cons by Brand")

        cols = st.columns(min(len(selected_brands), 3))
        for i, brand in enumerate(selected_brands):
            with cols[i % len(cols)]:
                st.markdown(f"#### {brand}")
                theme_data = themes.get(brand, {})

                pos = theme_data.get("positive_themes", [])[:5]
                neg = theme_data.get("negative_themes", [])[:5]

                if pos:
                    st.success("**Top Praise:**")
                    for p in pos:
                        kw = p["keyword"] if isinstance(p, dict) else str(p)
                        score = f" ({p['score']:.2f})" if isinstance(p, dict) and "score" in p else ""
                        st.markdown(f"  ✅ {kw}{score}")

                if neg:
                    st.error("**Top Complaints:**")
                    for n in neg:
                        kw = n["keyword"] if isinstance(n, dict) else str(n)
                        score = f" ({n['score']:.2f})" if isinstance(n, dict) and "score" in n else ""
                        st.markdown(f"  ❌ {kw}{score}")

    # ─── Value for Money (BONUS) ─────────────────────────────
    if vfm_data is not None:
        st.divider()
        st.markdown("### 💎 Value-for-Money Rankings")

        brand_vfm = vfm_data[vfm_data["brand"].isin(selected_brands)].groupby("brand").agg(
            avg_vfm=("vfm_score", "mean"),
            avg_price=("price", "mean"),
        ).reset_index().sort_values("avg_vfm", ascending=False)

        fig = create_brand_bar_chart(brand_vfm, "brand", "avg_vfm",
                                     title="Value-for-Money Score (Higher = Better Value)")
        fig.update_layout(yaxis_title="VFM Score")
        st.plotly_chart(fig, use_container_width=True)

    # ─── Price Band Analysis (BONUS) ─────────────────────────
    if price_bands is not None:
        st.divider()
        st.markdown("### 📊 Price Band Distribution")
        st.markdown("*How each brand is positioned across Budget / Mid-Range / Premium segments*")

        pb = price_bands[price_bands["brand"].isin(selected_brands)]
        if not pb.empty:
            fig = go.Figure()
            band_colors = {"Budget": "#34d399", "Mid-Range": "#38bdf8", "Premium": "#a78bfa"}
            for band in ["Budget", "Mid-Range", "Premium"]:
                bd = pb[pb["price_band"] == band]
                if not bd.empty:
                    fig.add_trace(go.Bar(
                        x=bd["brand"],
                        y=bd["product_count"],
                        name=band,
                        marker_color=band_colors.get(band, "#22d3ee"),
                        marker_opacity=0.85,
                        text=bd["product_count"],
                        textposition="inside",
                        textfont=dict(color="#030712"),
                    ))
            fig.update_layout(
                barmode="stack",
                title=dict(text="Products per Price Band", font=dict(size=15, color="#f1f5f9")),
                yaxis_title="Number of Products",
                height=400,
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Outfit, sans-serif", color="#94a3b8"),
            )
            st.plotly_chart(fig, use_container_width=True)
