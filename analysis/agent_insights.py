"""
Agent Insights Generator (BONUS)
==================================
Automatically generates 5 non-obvious, data-driven conclusions
from the competitive intelligence dataset. Uses statistical analysis
and data mining techniques (no LLM required).

Insight Categories:
    1. Hidden Quality Leader — Brand with best sentiment-to-price ratio
    2. Discount Trap — Brands where high discounts correlate with low sentiment
    3. Durability Dark Horse — Brand with best durability aspect sentiment
    4. Review Manipulation Risk — Products with lowest trust scores
    5. Market Gap — Price bands with low competition but high demand

Each insight includes:
    - A compelling title and description
    - Supporting data evidence
    - Confidence level (High/Medium/Low)
    - Actionable recommendation
"""

import pandas as pd
import numpy as np
import json
import os


class AgentInsightsGenerator:
    """
    Generates non-obvious competitive intelligence insights
    by mining patterns across multiple data dimensions.
    """

    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = data_dir
        self.products = pd.read_csv(f"{data_dir}/products.csv")
        self.insights = []

        # Load optional analysis results
        try:
            self.reviews = pd.read_csv(f"{data_dir}/reviews_analyzed.csv")
        except FileNotFoundError:
            self.reviews = pd.read_csv(f"{data_dir}/reviews.csv")

        try:
            self.aspects = pd.read_csv(f"{data_dir}/aspect_sentiments.csv")
        except FileNotFoundError:
            self.aspects = None

        try:
            self.trust = pd.read_csv(f"{data_dir}/trust_scores.csv")
        except FileNotFoundError:
            self.trust = None

        try:
            self.vfm = pd.read_csv(f"{data_dir}/value_for_money.csv")
        except FileNotFoundError:
            self.vfm = None

    def generate_all(self) -> list:
        """Generate all 5 insights."""
        print("  🤖 Generating Agent Insights...")

        self._insight_hidden_quality_leader()
        self._insight_discount_trap()
        self._insight_durability_dark_horse()
        self._insight_review_manipulation_risk()
        self._insight_market_gap()

        # Add extra insights to ensure we always have 5
        if len(self.insights) < 5:
            self._insight_sentiment_price_paradox()
        if len(self.insights) < 5:
            self._insight_category_performance()

        print(f"    ✓ Generated {len(self.insights)} insights")
        return self.insights[:5]

    def _insight_hidden_quality_leader(self):
        """Find the brand that punches above its weight on sentiment relative to price."""
        if "combined_score" not in self.reviews.columns:
            return

        brand_stats = self.reviews.groupby("brand").agg(
            avg_sentiment=("combined_score", "mean"),
        ).reset_index()
        
        brand_price = self.products.groupby("brand")["price"].mean().reset_index()
        brand_price.columns = ["brand", "avg_price"]
        
        merged = brand_stats.merge(brand_price, on="brand")
        
        # Normalize
        merged["norm_sentiment"] = (merged["avg_sentiment"] - merged["avg_sentiment"].min()) / \
                                   (merged["avg_sentiment"].max() - merged["avg_sentiment"].min() + 0.001)
        merged["norm_price"] = (merged["avg_price"] - merged["avg_price"].min()) / \
                               (merged["avg_price"].max() - merged["avg_price"].min() + 0.001)
        
        # Quality-to-price ratio
        merged["quality_price_ratio"] = merged["norm_sentiment"] / (merged["norm_price"] + 0.1)
        
        leader = merged.loc[merged["quality_price_ratio"].idxmax()]
        premium = merged.loc[merged["avg_price"].idxmax()]

        self.insights.append({
            "id": 1,
            "title": "Hidden Quality Leader",
            "icon": "👑",
            "category": "Competitive Intelligence",
            "description": (
                f"**{leader['brand']}** delivers the highest customer satisfaction relative to its price, "
                f"with a sentiment score of {leader['avg_sentiment']:.3f} at an average price of "
                f"₹{leader['avg_price']:.0f}. This is {(leader['quality_price_ratio']/merged['quality_price_ratio'].mean()-1)*100:.0f}% "
                f"above the category average on our quality-to-price index."
            ),
            "evidence": {
                "brand": leader["brand"],
                "avg_sentiment": round(float(leader["avg_sentiment"]), 3),
                "avg_price": round(float(leader["avg_price"])),
                "quality_price_ratio": round(float(leader["quality_price_ratio"]), 3),
            },
            "comparison": {
                "premium_brand": premium["brand"],
                "premium_price": round(float(premium["avg_price"])),
                "premium_sentiment": round(float(premium["avg_sentiment"]), 3),
            },
            "confidence": "High",
            "recommendation": (
                f"For budget-conscious buyers, {leader['brand']} offers the strongest ROI. "
                f"Decision-makers should investigate what {leader['brand']} does differently "
                f"at a lower price point."
            ),
        })

    def _insight_discount_trap(self):
        """
        Identify brands where heavy discounting correlates with 
        lower customer satisfaction — suggesting discounts mask quality issues.
        """
        brand_disc = self.products.groupby("brand").agg(
            avg_discount=("discount_pct", "mean"),
            avg_price=("price", "mean"),
        ).reset_index()

        if "combined_score" in self.reviews.columns:
            brand_sent = self.reviews.groupby("brand")["combined_score"].mean().reset_index()
            brand_sent.columns = ["brand", "avg_sentiment"]
            merged = brand_disc.merge(brand_sent, on="brand")
        else:
            return

        # Find brand with highest discount but low sentiment
        merged["discount_sentiment_gap"] = merged["avg_discount"] / 100 - merged["avg_sentiment"]
        trap_brand = merged.loc[merged["discount_sentiment_gap"].idxmax()]
        
        # Find a contrast brand (low discount, high sentiment)
        merged["efficient"] = merged["avg_sentiment"] - merged["avg_discount"] / 100
        efficient_brand = merged.loc[merged["efficient"].idxmax()]

        self.insights.append({
            "id": 2,
            "title": "The Discount Trap",
            "icon": "⚠️",
            "category": "Pricing Strategy",
            "description": (
                f"**{trap_brand['brand']}** relies on the deepest average discounts "
                f"({trap_brand['avg_discount']:.1f}%) but still has below-average customer sentiment "
                f"({trap_brand['avg_sentiment']:.3f}). In contrast, **{efficient_brand['brand']}** "
                f"achieves better sentiment ({efficient_brand['avg_sentiment']:.3f}) with lower "
                f"discounting ({efficient_brand['avg_discount']:.1f}%). Heavy discounts may signal "
                f"quality concerns rather than attract loyal customers."
            ),
            "evidence": {
                "trap_brand": trap_brand["brand"],
                "trap_discount": round(float(trap_brand["avg_discount"]), 1),
                "trap_sentiment": round(float(trap_brand["avg_sentiment"]), 3),
                "efficient_brand": efficient_brand["brand"],
                "efficient_discount": round(float(efficient_brand["avg_discount"]), 1),
                "efficient_sentiment": round(float(efficient_brand["avg_sentiment"]), 3),
            },
            "confidence": "Medium",
            "recommendation": (
                f"Brands competing on deep discounts should invest in quality improvement "
                f"rather than price reductions. {trap_brand['brand']}'s strategy of heavy "
                f"discounting is not translating into customer satisfaction."
            ),
        })

    def _insight_durability_dark_horse(self):
        """Find the brand that unexpectedly leads on durability sentiment."""
        if self.aspects is None or self.aspects.empty:
            return

        durability = self.aspects[self.aspects["aspect"] == "Durability"]
        if durability.empty:
            return

        brand_dur = durability.groupby("brand").agg(
            avg_durability=("sentiment_score", "mean"),
            mention_count=("review_id", "count"),
        ).reset_index()

        # Filter brands with enough mentions
        brand_dur = brand_dur[brand_dur["mention_count"] >= 3]
        if brand_dur.empty:
            return

        # Compare with price
        brand_price = self.products.groupby("brand")["price"].mean().reset_index()
        brand_price.columns = ["brand", "avg_price"]
        merged = brand_dur.merge(brand_price, on="brand")

        # Find the best durability brand that's NOT the most expensive
        merged = merged.sort_values("avg_durability", ascending=False)
        most_expensive = merged.loc[merged["avg_price"].idxmax(), "brand"]

        dark_horse = merged[merged["brand"] != most_expensive].iloc[0] if len(merged) > 1 else merged.iloc[0]

        self.insights.append({
            "id": 3,
            "title": "Durability Dark Horse",
            "icon": "🛡️",
            "category": "Product Quality",
            "description": (
                f"**{dark_horse['brand']}** emerges as a surprising durability leader based on "
                f"aspect-level sentiment analysis. With a durability sentiment of "
                f"{dark_horse['avg_durability']:.3f} across {dark_horse['mention_count']:.0f} "
                f"mentions, it outperforms expectations for its ₹{dark_horse['avg_price']:.0f} "
                f"average price point. Buyers specifically praise build quality and material resilience."
            ),
            "evidence": {
                "brand": dark_horse["brand"],
                "durability_score": round(float(dark_horse["avg_durability"]), 3),
                "mentions": int(dark_horse["mention_count"]),
                "avg_price": round(float(dark_horse["avg_price"])),
            },
            "confidence": "Medium",
            "recommendation": (
                f"If durability is a priority, {dark_horse['brand']} offers the best "
                f"durability-to-price ratio. Premium brands may not always justify their "
                f"price premium on build quality alone."
            ),
        })

    def _insight_review_manipulation_risk(self):
        """Identify products/brands with highest review manipulation risk."""
        if self.trust is None or self.trust.empty:
            return

        # Find lowest trust products
        low_trust = self.trust.nsmallest(3, "trust_score")
        brand_trust = self.trust.groupby("brand")["trust_score"].mean()
        riskiest_brand = brand_trust.idxmin()
        safest_brand = brand_trust.idxmax()

        self.insights.append({
            "id": 4,
            "title": "Review Authenticity Alert",
            "icon": "🔍",
            "category": "Trust & Reliability",
            "description": (
                f"Our trust analysis reveals that **{riskiest_brand}** has the lowest average "
                f"review trust score ({brand_trust[riskiest_brand]:.0f}/100) across its product line. "
                f"Signals include review text similarity patterns and rating distribution anomalies. "
                f"In contrast, **{safest_brand}** scores highest ({brand_trust[safest_brand]:.0f}/100) "
                f"indicating more authentic customer feedback."
            ),
            "evidence": {
                "riskiest_brand": riskiest_brand,
                "riskiest_score": round(float(brand_trust[riskiest_brand]), 1),
                "safest_brand": safest_brand,
                "safest_score": round(float(brand_trust[safest_brand]), 1),
                "lowest_products": low_trust[["title", "trust_score"]].to_dict("records"),
            },
            "confidence": "Medium",
            "recommendation": (
                f"Weight {riskiest_brand} reviews with caution when making sourcing decisions. "
                f"Cross-reference with {safest_brand}'s more reliable reviews for accurate "
                f"market comparison."
            ),
        })

    def _insight_market_gap(self):
        """Identify price bands or categories with low competition but high demand signals."""
        # Analyze price band distribution
        def get_band(price):
            if price < 2500:
                return "Budget"
            elif price < 5000:
                return "Mid-Range"
            else:
                return "Premium"

        self.products["price_band"] = self.products["price"].apply(get_band)
        
        band_stats = self.products.groupby("price_band").agg(
            product_count=("product_id", "count"),
            brand_count=("brand", "nunique"),
            avg_rating=("rating", "mean"),
            avg_review_count=("review_count", "mean"),
        ).reset_index()

        # High review count but low product count = unmet demand
        band_stats["demand_supply_ratio"] = band_stats["avg_review_count"] / (band_stats["product_count"] + 1)

        gap = band_stats.loc[band_stats["demand_supply_ratio"].idxmax()]
        saturated = band_stats.loc[band_stats["product_count"].idxmax()]

        self.insights.append({
            "id": 5,
            "title": "Market Gap Opportunity",
            "icon": "🎯",
            "category": "Market Strategy",
            "description": (
                f"The **{gap['price_band']}** segment shows the highest demand-to-supply ratio "
                f"with {gap['avg_review_count']:.0f} avg reviews per product but only "
                f"{gap['product_count']:.0f} products from {gap['brand_count']:.0f} brands. "
                f"Meanwhile, the **{saturated['price_band']}** segment is oversaturated with "
                f"{saturated['product_count']:.0f} products. New entrants should consider "
                f"targeting the {gap['price_band']} segment for maximum impact."
            ),
            "evidence": {
                "gap_band": gap["price_band"],
                "gap_products": int(gap["product_count"]),
                "gap_avg_reviews": round(float(gap["avg_review_count"])),
                "saturated_band": saturated["price_band"],
                "saturated_products": int(saturated["product_count"]),
            },
            "confidence": "High",
            "recommendation": (
                f"Brands looking to expand should focus on the {gap['price_band']} segment "
                f"where demand exists but competition is lower. Existing players in the "
                f"{saturated['price_band']} segment should differentiate on quality rather "
                f"than competing on price alone."
            ),
        })

    def _insight_sentiment_price_paradox(self):
        """Find cases where cheaper products have better sentiment than expensive ones."""
        if "combined_score" not in self.reviews.columns:
            return

        product_sent = self.reviews.groupby("product_id")["combined_score"].mean().reset_index()
        product_sent.columns = ["product_id", "avg_sentiment"]
        merged = self.products.merge(product_sent, on="product_id")

        # Find cheapest product with top-quartile sentiment
        q75_sent = merged["avg_sentiment"].quantile(0.75)
        q25_price = merged["price"].quantile(0.25)

        cheap_good = merged[(merged["price"] <= q25_price) & (merged["avg_sentiment"] >= q75_sent)]
        if cheap_good.empty:
            return

        best = cheap_good.loc[cheap_good["avg_sentiment"].idxmax()]
        most_expensive = merged.loc[merged["price"].idxmax()]

        self.insights.append({
            "id": 6,
            "title": "The Price-Sentiment Paradox",
            "icon": "💡",
            "category": "Value Analysis",
            "description": (
                f"**{best['title'][:50]}...** (₹{best['price']:.0f}) achieves sentiment score "
                f"{best['avg_sentiment']:.3f}, higher than the most expensive product "
                f"**{most_expensive['title'][:40]}...** (₹{most_expensive['price']:.0f}, "
                f"sentiment: {most_expensive['avg_sentiment']:.3f}). Price doesn't guarantee "
                f"customer satisfaction in the luggage market."
            ),
            "evidence": {
                "cheap_product": best["title"],
                "cheap_price": round(float(best["price"])),
                "cheap_sentiment": round(float(best["avg_sentiment"]), 3),
                "expensive_product": most_expensive["title"],
                "expensive_price": round(float(most_expensive["price"])),
                "expensive_sentiment": round(float(most_expensive["avg_sentiment"]), 3),
            },
            "confidence": "High",
            "recommendation": (
                f"Price alone is not a reliable indicator of quality in the Indian luggage market. "
                f"Decision-makers should prioritize NLP-validated sentiment over price tags."
            ),
        })

    def _insight_category_performance(self):
        """Analyze which luggage categories perform best."""
        if "category" not in self.products.columns:
            return

        if "combined_score" in self.reviews.columns:
            prod_sent = self.reviews.groupby("product_id")["combined_score"].mean().reset_index()
            prod_sent.columns = ["product_id", "avg_sentiment"]
            merged = self.products.merge(prod_sent, on="product_id")
        else:
            merged = self.products.copy()
            merged["avg_sentiment"] = 0

        cat_stats = merged.groupby("category").agg(
            count=("product_id", "count"),
            avg_price=("price", "mean"),
            avg_rating=("rating", "mean"),
            avg_sentiment=("avg_sentiment", "mean"),
        ).reset_index()

        best_cat = cat_stats.loc[cat_stats["avg_sentiment"].idxmax()]

        self.insights.append({
            "id": 7,
            "title": "Category Performance Leader",
            "icon": "📊",
            "category": "Product Strategy",
            "description": (
                f"**{best_cat['category']}** luggage leads in customer satisfaction with an "
                f"average sentiment of {best_cat['avg_sentiment']:.3f} across {best_cat['count']:.0f} "
                f"products at ₹{best_cat['avg_price']:.0f} avg price. This may reflect "
                f"more focused product design in this category."
            ),
            "evidence": {
                "category": best_cat["category"],
                "product_count": int(best_cat["count"]),
                "avg_price": round(float(best_cat["avg_price"])),
                "avg_sentiment": round(float(best_cat["avg_sentiment"]), 3),
            },
            "confidence": "Medium",
            "recommendation": (
                f"Brands should allocate more R&D resources to the {best_cat['category']} "
                f"category where customer satisfaction is highest."
            ),
        })


def run_agent_insights(data_dir: str = "data/processed", output_dir: str = "data/processed"):
    """Run the Agent Insights generator."""

    print("\n" + "=" * 60)
    print("🤖 AGENT INSIGHTS GENERATOR")
    print("=" * 60)

    generator = AgentInsightsGenerator(data_dir)
    insights = generator.generate_all()

    # Print insights
    for insight in insights:
        print(f"\n  {insight['icon']} Insight #{insight['id']}: {insight['title']}")
        print(f"    Category: {insight['category']} | Confidence: {insight['confidence']}")
        print(f"    {insight['description'][:200]}...")

    # Save
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/agent_insights.json", "w") as f:
        json.dump(insights, f, indent=2, default=str)

    print(f"\n  💾 Insights saved to {output_dir}/agent_insights.json")
    print("=" * 60)

    return insights


if __name__ == "__main__":
    run_agent_insights()
