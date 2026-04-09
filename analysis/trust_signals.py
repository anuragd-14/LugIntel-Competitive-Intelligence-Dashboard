"""
Review Trust Signals Analysis (BONUS)
======================================
Analyzes review authenticity and trustworthiness through:
1. Review text similarity detection (copy-paste / templated reviews)
2. Rating distribution skewness analysis
3. Verified purchase ratio analysis
4. Review length and pattern analysis
5. Composite trust score calculation

Each product receives a Trust Score (0-100) combining all signals.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


class TrustAnalyzer:
    """Analyzes reviews for authenticity and trust signals."""

    # Weights for composite trust score
    WEIGHTS = {
        "similarity": 0.30,      # Low similarity is good
        "distribution": 0.20,    # Natural distribution is good
        "verified": 0.25,        # High verified % is good
        "length_quality": 0.25,  # Varied, detailed reviews are good
    }

    def __init__(self, reviews_df: pd.DataFrame, products_df: pd.DataFrame):
        self.reviews = reviews_df.copy()
        self.products = products_df.copy()
        self.trust_scores = {}

    def analyze_all(self) -> pd.DataFrame:
        """Run all trust signal analyses and compute composite scores."""
        print("  🔐 Analyzing review trust signals...")

        results = []

        for pid in self.products["product_id"].unique():
            product_reviews = self.reviews[self.reviews["product_id"] == pid]
            
            if len(product_reviews) < 3:
                continue

            product = self.products[self.products["product_id"] == pid].iloc[0]

            # Individual trust signals
            sim_score = self._similarity_score(product_reviews)
            dist_score = self._distribution_score(product_reviews)
            ver_score = self._verified_score(product_reviews)
            len_score = self._length_quality_score(product_reviews)

            # Composite trust score (0-100)
            composite = (
                self.WEIGHTS["similarity"] * sim_score
                + self.WEIGHTS["distribution"] * dist_score
                + self.WEIGHTS["verified"] * ver_score
                + self.WEIGHTS["length_quality"] * len_score
            )

            results.append({
                "product_id": pid,
                "brand": product["brand"],
                "title": product["title"],
                "review_count": len(product_reviews),
                "similarity_score": round(sim_score, 1),
                "distribution_score": round(dist_score, 1),
                "verified_score": round(ver_score, 1),
                "length_quality_score": round(len_score, 1),
                "trust_score": round(composite, 1),
                "trust_level": self._classify_trust(composite),
            })

        trust_df = pd.DataFrame(results)

        if not trust_df.empty:
            # Print summary
            level_counts = trust_df["trust_level"].value_counts()
            print(f"    ✓ Trust levels: High={level_counts.get('High', 0)}, "
                  f"Medium={level_counts.get('Medium', 0)}, "
                  f"Low={level_counts.get('Low', 0)}")

        return trust_df

    def _similarity_score(self, reviews: pd.DataFrame) -> float:
        """
        Check for suspiciously similar reviews using TF-IDF cosine similarity.
        Returns 0-100 where 100 = all reviews are unique.
        """
        texts = reviews["text"].dropna().tolist()
        if len(texts) < 2:
            return 80.0

        try:
            vectorizer = TfidfVectorizer(max_features=100, stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(texts)
            sim_matrix = cosine_similarity(tfidf_matrix)

            # Get upper triangle (exclude self-similarity)
            upper_tri = sim_matrix[np.triu_indices_from(sim_matrix, k=1)]

            if len(upper_tri) == 0:
                return 80.0

            # High average similarity = suspicious
            avg_similarity = upper_tri.mean()
            max_similarity = upper_tri.max()

            # Score: lower similarity = higher trust
            # avg_sim of 0.0 → 100, avg_sim of 0.8+ → 20
            score = max(20, 100 - (avg_similarity * 100))

            # Penalize if any pair is extremely similar (>0.85)
            if max_similarity > 0.85:
                score *= 0.7

            return min(100, score)

        except Exception:
            return 70.0

    def _distribution_score(self, reviews: pd.DataFrame) -> float:
        """
        Analyze rating distribution naturalness.
        Natural reviews tend to be slightly left-skewed (more positive).
        Extreme bimodality (U-shape) suggests manipulation.
        Returns 0-100 where 100 = natural distribution.
        """
        ratings = reviews["rating"]
        
        if len(ratings) < 3:
            return 70.0

        # Check for bimodality
        extreme_pct = ((ratings == 5) | (ratings == 1)).mean()
        
        # Natural distributions have std between 0.5-1.5
        rating_std = ratings.std()
        
        # Calculate score
        score = 80.0

        # Penalize extreme bimodality
        if extreme_pct > 0.8:
            score -= 30
        elif extreme_pct > 0.6:
            score -= 15

        # Penalize very low variance (all same rating)
        if rating_std < 0.3:
            score -= 20
        elif rating_std < 0.5:
            score -= 10

        # Penalize very high variance
        if rating_std > 2.0:
            score -= 15

        return max(20, min(100, score))

    def _verified_score(self, reviews: pd.DataFrame) -> float:
        """
        Score based on verified purchase ratio.
        Returns 0-100 where 100 = all verified.
        """
        if "verified" not in reviews.columns:
            return 70.0

        verified_ratio = reviews["verified"].mean()
        # Scale: 100% verified = 100, 50% = 60, 0% = 20
        return max(20, 20 + (verified_ratio * 80))

    def _length_quality_score(self, reviews: pd.DataFrame) -> float:
        """
        Analyze review text quality based on length and variety.
        Good reviews are detailed and varied in length.
        Returns 0-100.
        """
        texts = reviews["text"].dropna()
        if len(texts) == 0:
            return 50.0

        lengths = texts.str.len()
        avg_length = lengths.mean()
        length_std = lengths.std()

        score = 70.0

        # Penalize very short average length (< 30 chars = likely fake)
        if avg_length < 30:
            score -= 25
        elif avg_length < 50:
            score -= 10
        elif avg_length > 100:
            score += 10

        # Reward variety in length (real reviews vary)
        if length_std > 50:
            score += 10
        elif length_std < 10:
            score -= 15
        
        # Penalize if too many reviews have exact same length
        length_mode_pct = lengths.value_counts().max() / len(lengths)
        if length_mode_pct > 0.5:
            score -= 15

        return max(20, min(100, score))

    def _classify_trust(self, score: float) -> str:
        """Classify trust score into levels."""
        if score >= 70:
            return "High"
        elif score >= 50:
            return "Medium"
        else:
            return "Low"


def run_trust_analysis(products_path, reviews_path, output_dir="data/processed"):
    """Run the full trust signals analysis."""
    import os

    print("\n" + "=" * 60)
    print("🔐 REVIEW TRUST SIGNAL ANALYSIS")
    print("=" * 60)

    products_df = pd.read_csv(products_path)
    reviews_df = pd.read_csv(reviews_path)

    analyzer = TrustAnalyzer(reviews_df, products_df)
    trust_df = analyzer.analyze_all()

    # Brand-level summary
    if not trust_df.empty:
        brand_trust = trust_df.groupby("brand").agg(
            avg_trust=("trust_score", "mean"),
            min_trust=("trust_score", "min"),
            max_trust=("trust_score", "max"),
        ).round(1)
        
        print("\n  📊 Brand Trust Summary:")
        for brand, row in brand_trust.iterrows():
            emoji = "🟢" if row["avg_trust"] >= 70 else ("🟡" if row["avg_trust"] >= 50 else "🔴")
            print(f"    {emoji} {brand:>20s}  │  Avg: {row['avg_trust']:.0f}  │  "
                  f"Range: {row['min_trust']:.0f}-{row['max_trust']:.0f}")

    # Save
    os.makedirs(output_dir, exist_ok=True)
    trust_df.to_csv(f"{output_dir}/trust_scores.csv", index=False)

    print(f"\n  💾 Trust scores saved to {output_dir}/trust_scores.csv")
    print("=" * 60)

    return trust_df


if __name__ == "__main__":
    run_trust_analysis("data/processed/products.csv", "data/processed/reviews.csv")
