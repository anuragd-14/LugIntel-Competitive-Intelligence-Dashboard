"""
Value-for-Money Analysis (BONUS)
=================================
Analyzes the relationship between price and customer sentiment
to identify best-value products and price band performance.

Methodology:
    1. Products are bucketed into price bands (Budget/Mid-range/Premium)
    2. Sentiment scores are compared across price bands per brand
    3. Value-for-money score = Normalized Sentiment / Normalized Price
    4. Rankings identify best-value products and overpriced/undervalued items
"""

import pandas as pd
import numpy as np


# ─── Price Band Definitions ──────────────────────────────────────
PRICE_BANDS = {
    "Budget": (0, 2500),
    "Mid-Range": (2500, 5000),
    "Premium": (5000, 15000),
}


class ValueAnalyzer:
    """Analyzes value-for-money across brands and price bands."""

    def __init__(self, products_df: pd.DataFrame, reviews_df: pd.DataFrame):
        self.products = products_df.copy()
        self.reviews = reviews_df.copy()

    def assign_price_bands(self) -> pd.DataFrame:
        """Assign price band labels to products."""
        def get_band(price):
            for band, (low, high) in PRICE_BANDS.items():
                if low <= price < high:
                    return band
            return "Premium"

        self.products["price_band"] = self.products["price"].apply(get_band)
        return self.products

    def calculate_value_scores(self) -> pd.DataFrame:
        """
        Calculate value-for-money scores for each product.
        
        VFM Score = (Normalized Sentiment + Normalized Rating) / Normalized Price
        Higher score = better value for money.
        """
        print("  💰 Calculating value-for-money scores...")

        self.assign_price_bands()

        # Aggregate review sentiment per product
        if "combined_score" in self.reviews.columns:
            product_sentiment = self.reviews.groupby("product_id").agg(
                avg_sentiment=("combined_score", "mean"),
                review_count=("review_id", "count"),
            ).reset_index()
        else:
            product_sentiment = self.reviews.groupby("product_id").agg(
                review_count=("review_id", "count"),
            ).reset_index()
            product_sentiment["avg_sentiment"] = 0.0

        # Merge
        merged = self.products.merge(product_sentiment, on="product_id", how="left")
        merged["avg_sentiment"] = merged["avg_sentiment"].fillna(0)

        # Normalize scores to 0-1 scale
        price_min, price_max = merged["price"].min(), merged["price"].max()
        merged["norm_price"] = (merged["price"] - price_min) / (price_max - price_min + 1)

        sent_min, sent_max = merged["avg_sentiment"].min(), merged["avg_sentiment"].max()
        if sent_max > sent_min:
            merged["norm_sentiment"] = (merged["avg_sentiment"] - sent_min) / (sent_max - sent_min)
        else:
            merged["norm_sentiment"] = 0.5

        rat_min, rat_max = merged["rating"].min(), merged["rating"].max()
        merged["norm_rating"] = (merged["rating"] - rat_min) / (rat_max - rat_min + 1)

        # VFM Score (avoid division by zero)
        merged["vfm_score"] = (
            (merged["norm_sentiment"] * 0.5 + merged["norm_rating"] * 0.5) /
            (merged["norm_price"] + 0.1)
        ).round(3)

        # Rank
        merged["vfm_rank"] = merged["vfm_score"].rank(ascending=False).astype(int)

        # Classify
        q75 = merged["vfm_score"].quantile(0.75)
        q25 = merged["vfm_score"].quantile(0.25)
        merged["vfm_label"] = merged["vfm_score"].apply(
            lambda x: "Excellent Value" if x >= q75
            else ("Good Value" if x >= q25 else "Below Average Value")
        )

        print(f"    ✓ Computed VFM scores for {len(merged)} products")
        return merged

    def get_brand_value_summary(self, vfm_df: pd.DataFrame) -> pd.DataFrame:
        """Summarize value-for-money by brand."""
        brand_vfm = vfm_df.groupby("brand").agg(
            avg_price=("price", "mean"),
            avg_sentiment=("avg_sentiment", "mean"),
            avg_vfm=("vfm_score", "mean"),
            best_vfm_product=("vfm_score", "idxmax"),
        ).round(3)

        # Get best product names
        for brand in brand_vfm.index:
            best_idx = brand_vfm.loc[brand, "best_vfm_product"]
            brand_vfm.loc[brand, "best_product_name"] = vfm_df.loc[best_idx, "title"]

        brand_vfm = brand_vfm.drop(columns=["best_vfm_product"])
        return brand_vfm.sort_values("avg_vfm", ascending=False)

    def get_price_band_analysis(self, vfm_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze sentiment distribution across price bands per brand."""
        band_analysis = vfm_df.groupby(["brand", "price_band"]).agg(
            product_count=("product_id", "count"),
            avg_price=("price", "mean"),
            avg_rating=("rating", "mean"),
            avg_sentiment=("avg_sentiment", "mean"),
            avg_vfm=("vfm_score", "mean"),
        ).round(3).reset_index()

        return band_analysis


def run_value_analysis(products_path, reviews_path, output_dir="data/processed"):
    """Run the full value-for-money analysis."""
    import os

    print("\n" + "=" * 60)
    print("💰 VALUE-FOR-MONEY ANALYSIS")
    print("=" * 60)

    products_df = pd.read_csv(products_path)
    reviews_df = pd.read_csv(reviews_path)

    analyzer = ValueAnalyzer(products_df, reviews_df)
    vfm_df = analyzer.calculate_value_scores()

    # Brand summary
    brand_vfm = analyzer.get_brand_value_summary(vfm_df)
    print("\n  📊 Brand Value-for-Money Ranking:")
    for brand, row in brand_vfm.iterrows():
        print(f"    💎 {brand:>20s}  │  VFM: {row['avg_vfm']:.3f}  │  "
              f"Avg Price: ₹{row['avg_price']:.0f}")

    # Price band analysis
    band_df = analyzer.get_price_band_analysis(vfm_df)

    # Top 5 best value products
    top5 = vfm_df.nlargest(5, "vfm_score")[["brand", "title", "price", "rating", "vfm_score"]]
    print("\n  🏆 Top 5 Best Value Products:")
    for _, row in top5.iterrows():
        print(f"    ★ {row['title'][:50]}... │ ₹{row['price']:.0f} │ {row['rating']:.1f}★ │ VFM: {row['vfm_score']:.3f}")

    # Save
    os.makedirs(output_dir, exist_ok=True)
    vfm_df.to_csv(f"{output_dir}/value_for_money.csv", index=False)
    brand_vfm.to_csv(f"{output_dir}/brand_vfm.csv")
    band_df.to_csv(f"{output_dir}/price_band_analysis.csv", index=False)

    print(f"\n  💾 VFM results saved to {output_dir}/")
    print("=" * 60)

    return vfm_df


if __name__ == "__main__":
    run_value_analysis("data/processed/products.csv", "data/processed/reviews_analyzed.csv")
