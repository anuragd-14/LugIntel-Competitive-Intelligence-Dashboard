"""
Anomaly Detection Module (BONUS)
=================================
Detects data anomalies and inconsistencies in product reviews:
1. High rating + negative sentiment mismatch
2. Suspicious rating distributions (J-curve / U-shape)
3. Durability complaints in highly-rated products
4. Price-to-quality outliers

Methodology:
    - Statistical analysis using IQR for outlier detection
    - Distribution shape analysis via skewness / kurtosis
    - Cross-referencing star ratings with NLP sentiment scores
"""

import pandas as pd
import numpy as np
from scipy import stats


class AnomalyDetector:
    """Detects anomalies and inconsistencies in review data."""

    def __init__(self, products_df: pd.DataFrame, reviews_df: pd.DataFrame):
        self.products = products_df
        self.reviews = reviews_df
        self.anomalies = []

    def detect_all(self) -> list:
        """Run all anomaly detection methods."""
        print("  🔎 Scanning for anomalies...")
        
        self.detect_rating_sentiment_mismatch()
        self.detect_suspicious_distributions()
        self.detect_durability_in_highrated()
        self.detect_price_quality_outliers()

        print(f"    ✓ Found {len(self.anomalies)} anomalies")
        return self.anomalies

    def detect_rating_sentiment_mismatch(self):
        """
        Flag products where star rating is high (>=4.0) but
        NLP sentiment score is low/negative.
        """
        if "combined_score" not in self.reviews.columns:
            return

        product_sentiment = self.reviews.groupby("product_id").agg(
            avg_sentiment=("combined_score", "mean"),
            avg_review_rating=("rating", "mean"),
        )

        # Merge with product data
        merged = self.products.merge(product_sentiment, on="product_id", how="left")

        # High rating (>=4.0) but negative sentiment (<0)
        mismatched = merged[
            (merged["rating"] >= 4.0) & (merged["avg_sentiment"] < 0.05)
        ]

        for _, row in mismatched.iterrows():
            self.anomalies.append({
                "type": "Rating-Sentiment Mismatch",
                "severity": "High",
                "product_id": row["product_id"],
                "brand": row["brand"],
                "title": row["title"],
                "detail": (
                    f"Product has {row['rating']:.1f}★ rating but negative avg sentiment "
                    f"({row['avg_sentiment']:.3f}). Reviews may not reflect the star rating."
                ),
                "metric": {
                    "star_rating": float(row["rating"]),
                    "sentiment_score": float(row["avg_sentiment"]),
                },
            })

    def detect_suspicious_distributions(self):
        """
        Flag products with bimodal rating distributions (many 5★ and 1★, 
        few in between) which may indicate review manipulation.
        """
        for pid in self.products["product_id"].unique():
            product_reviews = self.reviews[self.reviews["product_id"] == pid]
            if len(product_reviews) < 5:
                continue

            ratings = product_reviews["rating"]
            
            # Check for bimodal distribution (U-shape or J-curve)
            extreme_pct = ((ratings == 5) | (ratings == 1)).mean()
            middle_pct = ((ratings >= 2) & (ratings <= 4)).mean()

            # Also check kurtosis (negative kurtosis = flat/bimodal)
            if len(ratings) > 3:
                kurt = ratings.kurtosis()
            else:
                kurt = 0

            if extreme_pct > 0.75 and middle_pct < 0.25:
                product = self.products[self.products["product_id"] == pid].iloc[0]
                self.anomalies.append({
                    "type": "Suspicious Rating Distribution",
                    "severity": "Medium",
                    "product_id": pid,
                    "brand": product["brand"],
                    "title": product["title"],
                    "detail": (
                        f"{extreme_pct:.0%} of reviews are 5★ or 1★ with very few middle ratings. "
                        f"This bimodal pattern may indicate review manipulation."
                    ),
                    "metric": {
                        "extreme_pct": float(extreme_pct),
                        "middle_pct": float(middle_pct),
                        "kurtosis": float(kurt),
                    },
                })

    def detect_durability_in_highrated(self):
        """
        Flag highly-rated products that have specific durability complaints
        in their reviews.
        """
        durability_keywords = [
            "broke", "broken", "crack", "cracked", "damage", "damaged",
            "fell apart", "falling apart", "flimsy", "fragile", "snapped",
            "tore", "torn", "ripped", "defective",
        ]

        for pid in self.products["product_id"].unique():
            product = self.products[self.products["product_id"] == pid].iloc[0]
            
            if product["rating"] < 3.8:
                continue

            product_reviews = self.reviews[self.reviews["product_id"] == pid]
            
            # Search for durability keywords in reviews
            durability_complaints = 0
            complaint_examples = []
            for _, rev in product_reviews.iterrows():
                text = str(rev.get("text", "")).lower()
                for kw in durability_keywords:
                    if kw in text:
                        durability_complaints += 1
                        if len(complaint_examples) < 2:
                            complaint_examples.append(text[:120])
                        break

            complaint_ratio = durability_complaints / max(len(product_reviews), 1)

            if complaint_ratio >= 0.20:
                self.anomalies.append({
                    "type": "Hidden Durability Issues",
                    "severity": "High",
                    "product_id": pid,
                    "brand": product["brand"],
                    "title": product["title"],
                    "detail": (
                        f"Despite {product['rating']:.1f}★ average, {durability_complaints} of "
                        f"{len(product_reviews)} reviews ({complaint_ratio:.0%}) mention durability "
                        f"issues (breakage, damage, etc.)."
                    ),
                    "metric": {
                        "star_rating": float(product["rating"]),
                        "durability_complaint_count": durability_complaints,
                        "complaint_ratio": float(complaint_ratio),
                    },
                    "examples": complaint_examples,
                })

    def detect_price_quality_outliers(self):
        """
        Flag products that are statistical outliers in price-to-rating ratio.
        Uses IQR method to identify overpriced or underpriced items.
        """
        self.products["price_per_star"] = self.products["price"] / self.products["rating"]

        Q1 = self.products["price_per_star"].quantile(0.25)
        Q3 = self.products["price_per_star"].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = self.products[
            (self.products["price_per_star"] < lower_bound) |
            (self.products["price_per_star"] > upper_bound)
        ]

        for _, row in outliers.iterrows():
            is_overpriced = row["price_per_star"] > upper_bound
            self.anomalies.append({
                "type": "Price-Quality Outlier",
                "severity": "Low",
                "product_id": row["product_id"],
                "brand": row["brand"],
                "title": row["title"],
                "detail": (
                    f"{'Overpriced' if is_overpriced else 'Underpriced'}: ₹{row['price']:.0f} for "
                    f"{row['rating']:.1f}★ (₹{row['price_per_star']:.0f}/star). "
                    f"Normal range: ₹{lower_bound:.0f}-₹{upper_bound:.0f}/star."
                ),
                "metric": {
                    "price": float(row["price"]),
                    "rating": float(row["rating"]),
                    "price_per_star": float(row["price_per_star"]),
                    "is_overpriced": is_overpriced,
                },
            })


def run_anomaly_detection(products_path, reviews_path, output_dir="data/processed"):
    """Run the full anomaly detection pipeline."""
    import os
    import json

    print("\n" + "=" * 60)
    print("🔎 ANOMALY DETECTION")
    print("=" * 60)

    products_df = pd.read_csv(products_path)
    reviews_df = pd.read_csv(reviews_path)

    detector = AnomalyDetector(products_df, reviews_df)
    anomalies = detector.detect_all()

    # Print summary
    if anomalies:
        type_counts = {}
        for a in anomalies:
            type_counts[a["type"]] = type_counts.get(a["type"], 0) + 1

        print("\n  📊 Anomaly Summary:")
        for atype, count in type_counts.items():
            print(f"    ⚠ {atype}: {count} found")

    # Save
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/anomalies.json", "w") as f:
        json.dump(anomalies, f, indent=2, default=str)

    print(f"\n  💾 Anomaly results saved to {output_dir}/anomalies.json")
    print("=" * 60)

    return anomalies


if __name__ == "__main__":
    run_anomaly_detection("data/processed/products.csv", "data/processed/reviews_analyzed.csv")
