"""
Agent Insights Page (BONUS)
=============================
AI-powered competitive intelligence insights section.
Displays 5 non-obvious, auto-generated conclusions from the data:
1. Hidden Quality Leader
2. The Discount Trap
3. Durability Dark Horse
4. Review Authenticity Alert
5. Market Gap Opportunity

Also includes:
- Anomaly alerts dashboard
- Value-for-money rankings
- Trust score overview
"""

import streamlit as st
import pandas as pd
import numpy as np
from dashboard.components.charts import (
    create_brand_bar_chart, create_trust_gauge, create_scatter_plot,
    BRAND_COLORS, apply_chart_style
)
import plotly.graph_objects as go


def render_agent_insights(insights, anomalies, vfm_data, trust_scores,
                         products, reviews, brand_sentiment):
    """Render the Agent Insights page."""

    # ─── Header ──────────────────────────────────────────────
    st.markdown("# 🤖 Agent Insights")
    st.markdown(
        "Auto-generated competitive intelligence insights powered by statistical analysis "
        "and data mining. These are **non-obvious conclusions** extracted from the dataset."
    )

    st.info(
        "💡 **How this works:** Our analysis engine cross-references pricing data, "
        "sentiment scores, aspect-level sentiment, trust signals, and market structure "
        "to surface insights that aren't visible from individual charts alone.",
        icon="🧠"
    )

    st.divider()

    # ─── Insight Cards ───────────────────────────────────────
    st.markdown("## 🔮 Top 5 Strategic Insights")

    if insights:
        for i, insight in enumerate(insights[:5]):
            icon = insight.get("icon", "💡")
            title = insight.get("title", f"Insight #{i+1}")
            category = insight.get("category", "General")
            confidence = insight.get("confidence", "Medium")
            description = insight.get("description", "")
            recommendation = insight.get("recommendation", "")
            evidence = insight.get("evidence", {})

            # Confidence badge
            conf_colors = {"High": "🟢", "Medium": "🟡", "Low": "🟠"}
            conf_badge = conf_colors.get(confidence, "⚪")

            with st.container():
                st.markdown(f"### {icon} Insight #{i+1}: {title}")
                
                meta_cols = st.columns([2, 2, 6])
                with meta_cols[0]:
                    st.caption(f"📂 {category}")
                with meta_cols[1]:
                    st.caption(f"{conf_badge} Confidence: {confidence}")

                st.markdown(description)

                if recommendation:
                    st.success(f"**💡 Recommendation:** {recommendation}")

                # Show evidence in expander
                if evidence:
                    with st.expander("📊 View Supporting Data"):
                        ev_cols = st.columns(min(len(evidence), 4))
                        for j, (key, val) in enumerate(evidence.items()):
                            if isinstance(val, (int, float, str)):
                                with ev_cols[j % len(ev_cols)]:
                                    label = key.replace("_", " ").title()
                                    if isinstance(val, float):
                                        st.metric(label, f"{val:,.3f}" if abs(val) < 10 else f"{val:,.0f}")
                                    else:
                                        st.metric(label, str(val))

                # Show comparison if available
                comparison = insight.get("comparison", {})
                if comparison:
                    with st.expander("⚔️ View Comparison"):
                        comp_cols = st.columns(min(len(comparison), 4))
                        for j, (key, val) in enumerate(comparison.items()):
                            with comp_cols[j % len(comp_cols)]:
                                label = key.replace("_", " ").title()
                                if isinstance(val, float):
                                    st.metric(label, f"{val:,.3f}" if abs(val) < 10 else f"₹{val:,.0f}")
                                else:
                                    st.metric(label, str(val))

                st.divider()
    else:
        st.warning("No insights available. Please run the analysis pipeline first.")

    # ─── Anomaly Dashboard ───────────────────────────────────
    st.markdown("## ⚠️ Anomaly Alerts")

    if anomalies:
        # Summary metrics
        severity_counts = {}
        type_counts = {}
        for a in anomalies:
            severity_counts[a["severity"]] = severity_counts.get(a["severity"], 0) + 1
            type_counts[a["type"]] = type_counts.get(a["type"], 0) + 1

        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            st.metric("Total Anomalies", len(anomalies))
        with ac2:
            st.metric("🔴 High Severity", severity_counts.get("High", 0))
        with ac3:
            st.metric("🟡 Medium Severity", severity_counts.get("Medium", 0))

        # Anomaly list
        for anomaly in anomalies:
            severity_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟠"}.get(anomaly["severity"], "⚪")
            
            with st.expander(
                f"{severity_icon} {anomaly['type']} — {anomaly.get('brand', 'Unknown')} | "
                f"{anomaly.get('title', '')[:60]}..."
            ):
                st.markdown(f"**Severity:** {anomaly['severity']}")
                st.markdown(f"**Product:** {anomaly.get('title', 'N/A')}")
                st.markdown(f"**Detail:** {anomaly['detail']}")

                if anomaly.get("metric"):
                    st.json(anomaly["metric"])

                if anomaly.get("examples"):
                    st.markdown("**Review Excerpts:**")
                    for ex in anomaly["examples"]:
                        st.caption(f'> "{ex}"')
    else:
        st.success("✅ No anomalies detected in the current dataset.")

    # ─── Value for Money Rankings ────────────────────────────
    if vfm_data is not None:
        st.divider()
        st.markdown("## 💎 Value-for-Money Rankings")
        st.markdown("*Products ranked by how much customer satisfaction they deliver per rupee spent.*")

        col1, col2 = st.columns(2)

        with col1:
            # Top 10 Best Value
            st.markdown("### 🏆 Top 10 Best Value Products")
            top10 = vfm_data.nlargest(10, "vfm_score")[
                ["brand", "title", "price", "rating", "vfm_score", "vfm_label"]
            ].copy()
            top10.columns = ["Brand", "Product", "Price", "Rating", "VFM Score", "Label"]
            top10["Price"] = top10["Price"].apply(lambda x: f"₹{x:,.0f}")
            top10["Rating"] = top10["Rating"].apply(lambda x: f"{x:.1f} ⭐")
            top10["VFM Score"] = top10["VFM Score"].round(3)
            st.dataframe(top10, use_container_width=True, hide_index=True, height=400)

        with col2:
            # Bottom 10
            st.markdown("### 📉 Lowest Value Products")
            bottom10 = vfm_data.nsmallest(10, "vfm_score")[
                ["brand", "title", "price", "rating", "vfm_score", "vfm_label"]
            ].copy()
            bottom10.columns = ["Brand", "Product", "Price", "Rating", "VFM Score", "Label"]
            bottom10["Price"] = bottom10["Price"].apply(lambda x: f"₹{x:,.0f}")
            bottom10["Rating"] = bottom10["Rating"].apply(lambda x: f"{x:.1f} ⭐")
            bottom10["VFM Score"] = bottom10["VFM Score"].round(3)
            st.dataframe(bottom10, use_container_width=True, hide_index=True, height=400)

        # VFM scatter
        if "avg_sentiment" in vfm_data.columns:
            st.markdown("### 📊 Price vs Value-for-Money Score")
            fig = create_scatter_plot(
                vfm_data, "price", "vfm_score", "brand",
                title=""
            )
            fig.update_layout(
                xaxis_title="Price (₹)",
                yaxis_title="Value-for-Money Score",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ─── Trust Overview ──────────────────────────────────────
    if trust_scores is not None and not trust_scores.empty:
        st.divider()
        st.markdown("## 🔐 Review Trust Overview")

        brand_trust = trust_scores.groupby("brand").agg(
            avg_trust=("trust_score", "mean"),
            min_trust=("trust_score", "min"),
            products_analyzed=("product_id", "count"),
        ).reset_index().sort_values("avg_trust", ascending=False)

        trust_cols = st.columns(len(brand_trust))
        for i, (_, row) in enumerate(brand_trust.iterrows()):
            with trust_cols[i]:
                fig = create_trust_gauge(row["avg_trust"], row["brand"])
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"📦 {row['products_analyzed']:.0f} products analyzed")

        # Low trust products alert
        low_trust = trust_scores[trust_scores["trust_score"] < 60]
        if not low_trust.empty:
            st.warning(
                f"⚠️ **{len(low_trust)} products** have trust scores below 60/100. "
                f"Review these products carefully before making sourcing decisions."
            )
            st.dataframe(
                low_trust[["brand", "title", "trust_score", "trust_level", "similarity_score",
                          "distribution_score", "verified_score"]].sort_values("trust_score"),
                use_container_width=True,
                hide_index=True,
            )

    # ─── Decision-Maker Summary ──────────────────────────────
    st.divider()
    st.markdown("## 📋 Decision-Maker Summary")

    if brand_sentiment is not None:
        bs = brand_sentiment.reset_index()
        best_sentiment = bs.loc[bs["avg_sentiment"].idxmax()]
        worst_sentiment = bs.loc[bs["avg_sentiment"].idxmin()]

        best_value_brand = ""
        if vfm_data is not None:
            bv = vfm_data.groupby("brand")["vfm_score"].mean()
            best_value_brand = bv.idxmax()

        cheapest = products.groupby("brand")["price"].mean().idxmin()
        most_reviewed = products.groupby("brand")["review_count"].sum().idxmax()

        st.markdown(f"""
| Dimension | Winner | Details |
|-----------|--------|---------|
| 🏆 **Best Sentiment** | {best_sentiment['brand']} | Score: {best_sentiment['avg_sentiment']:.3f}, {best_sentiment['positive_pct']:.0f}% positive reviews |
| 📉 **Lowest Sentiment** | {worst_sentiment['brand']} | Score: {worst_sentiment['avg_sentiment']:.3f}, {worst_sentiment['negative_pct']:.0f}% negative reviews |
| 💰 **Most Affordable** | {cheapest} | Avg ₹{products.groupby('brand')['price'].mean()[cheapest]:,.0f} |
| 💬 **Most Reviewed** | {most_reviewed} | {products.groupby('brand')['review_count'].sum()[most_reviewed]:,} total reviews |
| 💎 **Best Value** | {best_value_brand if best_value_brand else 'N/A'} | Highest sentiment-to-price ratio |
        """)

        st.info(
            "**Key Takeaway:** High price does not guarantee high satisfaction. "
            f"**{best_value_brand or best_sentiment['brand']}** delivers the strongest overall value "
            f"proposition in the Indian luggage market, while premium brands like "
            f"**{products.groupby('brand')['price'].mean().idxmax()}** need to better "
            f"justify their price premium through product quality improvements."
        )
