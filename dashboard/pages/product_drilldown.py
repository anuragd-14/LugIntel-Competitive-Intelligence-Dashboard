"""
Product Drilldown Page
=======================
Detailed view of individual products with:
- Product selector (brand → product)
- Product summary card (price, rating, discount, reviews)
- Sentiment distribution (pie chart)
- Review synthesis (themes, word cloud)
- Individual review browser with sentiment tags
- Trust score indicator (BONUS)
- Anomaly alerts (BONUS)
"""

import streamlit as st
import pandas as pd
import numpy as np
from dashboard.components.charts import (
    create_pie_chart, create_sentiment_gauge, create_trust_gauge,
    BRAND_COLORS, SENTIMENT_COLORS, apply_chart_style
)
import plotly.graph_objects as go


def render_product_drilldown(products, reviews, trust_scores, anomalies,
                             aspect_sentiments, themes):
    """Render the Product Drilldown page."""

    # ─── Header ──────────────────────────────────────────────
    st.markdown("# 🔍 Product Drilldown")
    st.markdown(
        "Deep-dive into individual products. Explore reviews, sentiment, "
        "pricing, and quality signals at the product level."
    )
    st.divider()

    # ─── Filters ─────────────────────────────────────────────
    col1, col2 = st.columns([1, 3])

    with col1:
        selected_brand = st.selectbox(
            "🏷️ Select Brand",
            options=sorted(products["brand"].unique()),
            key="drill_brand",
        )

    brand_products = products[products["brand"] == selected_brand].sort_values("title")

    with col2:
        selected_product = st.selectbox(
            "📦 Select Product",
            options=brand_products["title"].tolist(),
            key="drill_product",
        )

    product = brand_products[brand_products["title"] == selected_product].iloc[0]
    pid = product["product_id"]
    product_reviews = reviews[reviews["product_id"] == pid]

    st.divider()

    # ─── Product Summary Card ────────────────────────────────
    st.markdown(f"### {product['title']}")

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.metric("💰 Price", f"₹{product['price']:,.0f}")
    with k2:
        st.metric("🏷️ MRP", f"₹{product['list_price']:,.0f}")
    with k3:
        st.metric("📉 Discount", f"{product['discount_pct']:.1f}%")
    with k4:
        st.metric("⭐ Rating", f"{product['rating']:.1f}/5.0")
    with k5:
        st.metric("💬 Reviews", f"{product['review_count']:,}")

    # Category & size info
    cat_info = []
    if "category" in product and pd.notna(product["category"]):
        cat_info.append(f"**Category:** {product['category']}")
    if "size" in product and pd.notna(product["size"]):
        cat_info.append(f"**Size:** {product['size']}")
    cat_info.append(f"**Brand:** {selected_brand}")
    st.markdown(" | ".join(cat_info))

    st.divider()

    # ─── Sentiment Analysis ──────────────────────────────────
    if not product_reviews.empty and "sentiment_label" in product_reviews.columns:
        st.markdown("### 😊 Sentiment Analysis")

        col1, col2 = st.columns([1, 1])

        with col1:
            # Sentiment distribution pie
            sent_counts = product_reviews["sentiment_label"].value_counts()
            fig = create_pie_chart(
                sent_counts.index.tolist(),
                sent_counts.values.tolist(),
                title="Review Sentiment Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Sentiment gauge
            if "combined_score" in product_reviews.columns:
                avg_sent = product_reviews["combined_score"].mean()
                fig = create_sentiment_gauge(avg_sent, title="Average Sentiment Score")
                st.plotly_chart(fig, use_container_width=True)

                # Comparison with brand average
                brand_reviews = reviews[reviews["brand"] == selected_brand]
                brand_avg = brand_reviews["combined_score"].mean()
                diff = avg_sent - brand_avg
                if diff > 0:
                    st.success(f"📈 +{diff:.3f} above {selected_brand} brand average ({brand_avg:+.3f})")
                else:
                    st.warning(f"📉 {diff:.3f} below {selected_brand} brand average ({brand_avg:+.3f})")

        # Rating distribution bar chart
        st.markdown("#### ⭐ Rating Distribution")
        rating_counts = product_reviews["rating"].value_counts().sort_index()
        
        rating_colors = {1: "#f87171", 2: "#fb923c", 3: "#fbbf24", 4: "#a3e635", 5: "#34d399"}
        fig = go.Figure(go.Bar(
            x=[f"{r} ⭐" for r in rating_counts.index],
            y=rating_counts.values,
            marker_color=[rating_colors.get(r, "#22d3ee") for r in rating_counts.index],
            marker_opacity=0.9,
            text=rating_counts.values,
            textposition="outside",
            textfont=dict(color="#e2e8f0"),
        ))
        fig.update_layout(
            yaxis_title="Number of Reviews",
            height=300,
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Outfit, sans-serif", color="#94a3b8"),
            margin=dict(l=40, r=40, t=20, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ─── Aspect Sentiment (BONUS) ────────────────────────────
    if aspect_sentiments is not None:
        product_aspects = aspect_sentiments[aspect_sentiments["product_id"] == pid]
        if not product_aspects.empty:
            st.divider()
            st.markdown("### 🔬 Aspect-Level Sentiment")
            st.markdown("*How customers feel about specific product attributes*")

            aspect_agg = product_aspects.groupby("aspect").agg(
                avg_sentiment=("sentiment_score", "mean"),
                mention_count=("review_id", "count"),
            ).reset_index().sort_values("avg_sentiment", ascending=True)

            fig = go.Figure()
            colors = []
            for _, row in aspect_agg.iterrows():
                if row["avg_sentiment"] > 0.1:
                    colors.append("#34d399")
                elif row["avg_sentiment"] < -0.1:
                    colors.append("#f87171")
                else:
                    colors.append("#fbbf24")

            fig.add_trace(go.Bar(
                y=aspect_agg["aspect"],
                x=aspect_agg["avg_sentiment"],
                orientation="h",
                marker_color=colors,
                marker_opacity=0.9,
                text=aspect_agg.apply(
                    lambda r: f"{r['avg_sentiment']:+.3f} ({r['mention_count']:.0f} mentions)",
                    axis=1
                ),
                textposition="outside",
                textfont=dict(size=11, color="#e2e8f0"),
            ))
            fig.update_layout(
                xaxis_title="Sentiment Score",
                xaxis_range=[-0.6, 0.8],
                height=320,
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Outfit, sans-serif", color="#94a3b8"),
                margin=dict(l=120, r=100, t=20, b=40),
            )
            fig.add_vline(x=0, line_dash="dash", line_color="rgba(34,211,238,0.2)")
            st.plotly_chart(fig, use_container_width=True)

    # ─── Trust Score (BONUS) ─────────────────────────────────
    if trust_scores is not None:
        product_trust = trust_scores[trust_scores["product_id"] == pid]
        if not product_trust.empty:
            st.divider()
            st.markdown("### 🔐 Review Trust Analysis")

            trust_row = product_trust.iloc[0]

            tc1, tc2, tc3, tc4, tc5 = st.columns(5)
            with tc1:
                fig = create_trust_gauge(trust_row["trust_score"], "Overall Trust")
                st.plotly_chart(fig, use_container_width=True)
            with tc2:
                st.metric("📝 Text Similarity", f"{trust_row['similarity_score']:.0f}/100")
            with tc3:
                st.metric("📊 Distribution", f"{trust_row['distribution_score']:.0f}/100")
            with tc4:
                st.metric("✅ Verified", f"{trust_row['verified_score']:.0f}/100")
            with tc5:
                st.metric("📏 Review Quality", f"{trust_row['length_quality_score']:.0f}/100")

            trust_level = trust_row["trust_level"]
            if trust_level == "High":
                st.success(f"🟢 Trust Level: **{trust_level}** — Reviews appear authentic and reliable.")
            elif trust_level == "Medium":
                st.warning(f"🟡 Trust Level: **{trust_level}** — Some trust signals raised minor concerns.")
            else:
                st.error(f"🔴 Trust Level: **{trust_level}** — Multiple trust signals indicate potential manipulation.")

    # ─── Anomaly Alerts (BONUS) ──────────────────────────────
    if anomalies:
        product_anomalies = [a for a in anomalies if a.get("product_id") == pid]
        if product_anomalies:
            st.divider()
            st.markdown("### ⚠️ Anomaly Alerts")
            for anomaly in product_anomalies:
                severity_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟠"}.get(anomaly["severity"], "⚪")
                st.warning(f"{severity_icon} **{anomaly['type']}** (Severity: {anomaly['severity']})\n\n"
                          f"{anomaly['detail']}")

    # ─── Review Browser ──────────────────────────────────────
    st.divider()
    st.markdown("### 💬 Customer Reviews")

    if not product_reviews.empty:
        # Sort options
        sort_option = st.selectbox(
            "Sort by",
            ["Most Recent", "Highest Rating", "Lowest Rating", "Most Helpful"],
            key="review_sort"
        )

        sorted_reviews = product_reviews.copy()
        if sort_option == "Most Recent":
            if "date" in sorted_reviews.columns:
                sorted_reviews = sorted_reviews.sort_values("date", ascending=False)
        elif sort_option == "Highest Rating":
            sorted_reviews = sorted_reviews.sort_values("rating", ascending=False)
        elif sort_option == "Lowest Rating":
            sorted_reviews = sorted_reviews.sort_values("rating", ascending=True)
        elif sort_option == "Most Helpful":
            if "helpful_count" in sorted_reviews.columns:
                sorted_reviews = sorted_reviews.sort_values("helpful_count", ascending=False)

        # Display reviews
        for _, rev in sorted_reviews.head(20).iterrows():
            rating = int(rev["rating"]) if pd.notna(rev.get("rating")) else 0
            stars = "⭐" * rating + "☆" * (5 - rating)

            # Sentiment badge
            sent_badge = ""
            if "sentiment_label" in rev and pd.notna(rev.get("sentiment_label")):
                badge_colors = {"Positive": "🟢", "Neutral": "🟡", "Negative": "🔴"}
                sent_badge = f" {badge_colors.get(rev['sentiment_label'], '')} {rev['sentiment_label']}"

            verified = " ✅ Verified" if rev.get("verified") else ""
            date_str = f" | {rev['date']}" if pd.notna(rev.get("date")) else ""

            title = rev.get("title", "")
            text = rev.get("text", "")

            with st.expander(f"{stars} **{title}**{sent_badge}{verified}{date_str}"):
                st.write(text)

                if "combined_score" in rev and pd.notna(rev.get("combined_score")):
                    score = rev["combined_score"]
                    st.caption(
                        f"Sentiment: {score:+.3f} | "
                        f"VADER: {rev.get('vader_compound', 'N/A')} | "
                        f"TextBlob: {rev.get('textblob_polarity', 'N/A')}"
                    )

                if pd.notna(rev.get("helpful_count")) and rev["helpful_count"] > 0:
                    st.caption(f"👍 {int(rev['helpful_count'])} people found this helpful")
    else:
        st.info("No reviews available for this product.")

    # ─── Product Comparison Quick-View ───────────────────────
    st.divider()
    st.markdown("### 📊 All Products from This Brand")

    brand_prod_table = products[products["brand"] == selected_brand][
        ["title", "price", "list_price", "discount_pct", "rating", "review_count"]
    ].copy()
    brand_prod_table.columns = ["Product", "Price (₹)", "MRP (₹)", "Discount %", "Rating", "Reviews"]

    # Highlight selected product
    st.dataframe(
        brand_prod_table,
        use_container_width=True,
        hide_index=True,
        height=min(400, 35 * len(brand_prod_table) + 50),
    )
