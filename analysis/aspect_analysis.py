"""
Aspect-Level Sentiment Analysis (BONUS)
========================================
Performs fine-grained sentiment analysis at the aspect level.
Identifies and scores sentiment for specific luggage attributes:
wheels, handle, material, zipper, size/capacity, durability, weight, lock.

Methodology:
    1. Sentence tokenization of review text
    2. Aspect detection via curated keyword dictionaries
    3. VADER sentiment scoring on aspect-containing sentences
    4. Aggregation to product and brand level
"""

import pandas as pd
import numpy as np
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# ─── Aspect Dictionaries ─────────────────────────────────────────
# Curated keyword sets for each luggage aspect
ASPECT_KEYWORDS = {
    "Wheels": [
        "wheel", "wheels", "rolling", "roller", "spinner", "spinners",
        "caster", "casters", "rotation", "rotate", "glide", "smooth roll",
        "360", "swivel",
    ],
    "Handle": [
        "handle", "handles", "grip", "grips", "telescopic", "retractable",
        "trolley handle", "pull handle", "push handle", "extend", "handlebar",
    ],
    "Material": [
        "material", "fabric", "polycarbonate", "hardside", "hardshell",
        "softside", "nylon", "polyester", "abs", "plastic", "build", "body",
        "finish", "surface", "texture", "shell", "outer",
    ],
    "Zipper": [
        "zipper", "zippers", "zip", "zips", "closure", "chain",
        "ykk", "zip quality", "unzip", "stuck zip", "broken zip",
    ],
    "Size & Capacity": [
        "size", "capacity", "spacious", "roomy", "compartment", "compartments",
        "pocket", "pockets", "storage", "space", "internal", "interior",
        "expandable", "cabin size", "fits", "packing",
    ],
    "Durability": [
        "durable", "durability", "sturdy", "robust", "strong", "break",
        "broke", "broken", "crack", "cracked", "damage", "damaged",
        "lasting", "withstand", "survive", "tough", "flimsy", "fragile",
        "quality", "build quality", "long lasting",
    ],
    "Weight": [
        "weight", "lightweight", "light weight", "heavy", "heavier",
        "lighter", "weighs", "kg", "kilogram", "portable", "easy to carry",
    ],
    "Lock": [
        "lock", "locks", "tsa", "combination", "combination lock",
        "number lock", "security", "secure", "locking", "key",
    ],
}


class AspectAnalyzer:
    """
    Performs aspect-level sentiment analysis on product reviews.
    
    For each review, identifies which aspects are mentioned and
    determines the sentiment expressed toward each aspect.
    """

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.aspect_patterns = self._compile_patterns()

    def _compile_patterns(self) -> dict:
        """Pre-compile regex patterns for each aspect."""
        patterns = {}
        for aspect, keywords in ASPECT_KEYWORDS.items():
            # Sort by length descending to match longer phrases first
            sorted_kw = sorted(keywords, key=len, reverse=True)
            pattern = re.compile(
                r'\b(' + '|'.join(re.escape(kw) for kw in sorted_kw) + r')\b',
                re.IGNORECASE
            )
            patterns[aspect] = pattern
        return patterns

    def _split_sentences(self, text: str) -> list:
        """Split text into sentences."""
        if not text:
            return []
        sentences = re.split(r'[.!?]+', str(text))
        return [s.strip() for s in sentences if len(s.strip()) > 5]

    def analyze_review(self, text: str) -> list:
        """
        Analyze a single review for aspect-level sentiments.
        
        Returns:
            List of dicts: [{aspect, keyword_matched, sentence, sentiment_score}, ...]
        """
        if not text or not isinstance(text, str):
            return []

        results = []
        sentences = self._split_sentences(text)

        for sentence in sentences:
            for aspect, pattern in self.aspect_patterns.items():
                match = pattern.search(sentence)
                if match:
                    # Score sentiment of the sentence containing the aspect
                    vader_score = self.vader.polarity_scores(sentence)
                    results.append({
                        "aspect": aspect,
                        "keyword_matched": match.group(0).lower(),
                        "sentence": sentence,
                        "sentiment_score": round(vader_score["compound"], 4),
                    })

        return results

    def analyze_all_reviews(self, reviews_df: pd.DataFrame) -> pd.DataFrame:
        """
        Run aspect-level analysis on all reviews.
        
        Returns:
            DataFrame with columns: review_id, product_id, brand, aspect,
                                   keyword_matched, sentence, sentiment_score
        """
        print("  🔬 Running aspect-level sentiment analysis...")

        all_aspects = []

        for _, row in reviews_df.iterrows():
            full_text = f"{row.get('title', '')}. {row.get('text', '')}"
            aspects = self.analyze_review(full_text)

            for asp in aspects:
                asp["review_id"] = row.get("review_id", "")
                asp["product_id"] = row.get("product_id", "")
                asp["brand"] = row.get("brand", "")
                all_aspects.append(asp)

        aspects_df = pd.DataFrame(all_aspects)

        if not aspects_df.empty:
            print(f"    ✓ Found {len(aspects_df)} aspect mentions across {aspects_df['aspect'].nunique()} aspects")
            
            # Print aspect distribution
            aspect_counts = aspects_df["aspect"].value_counts()
            for aspect, count in aspect_counts.items():
                avg_sent = aspects_df[aspects_df["aspect"] == aspect]["sentiment_score"].mean()
                emoji = "🟢" if avg_sent > 0.1 else ("🟡" if avg_sent > -0.1 else "🔴")
                print(f"      {emoji} {aspect:>18s}: {count:>4d} mentions | avg sentiment: {avg_sent:+.3f}")

        return aspects_df

    def get_brand_aspect_matrix(self, aspects_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create a brand × aspect sentiment matrix for heatmap visualization.
        
        Returns:
            DataFrame with brands as rows, aspects as columns, avg sentiment as values.
        """
        if aspects_df.empty:
            return pd.DataFrame()

        matrix = aspects_df.pivot_table(
            index="brand",
            columns="aspect",
            values="sentiment_score",
            aggfunc="mean"
        ).round(3)

        return matrix

    def get_aspect_summary(self, aspects_df: pd.DataFrame) -> dict:
        """
        Generate a comprehensive aspect summary per brand.
        
        Returns:
            dict: {brand: {aspect: {avg_score, count, top_positive, top_negative}}}
        """
        summary = {}

        for brand in aspects_df["brand"].unique():
            brand_data = aspects_df[aspects_df["brand"] == brand]
            brand_summary = {}

            for aspect in ASPECT_KEYWORDS.keys():
                aspect_data = brand_data[brand_data["aspect"] == aspect]
                if aspect_data.empty:
                    continue

                pos = aspect_data[aspect_data["sentiment_score"] > 0.1]
                neg = aspect_data[aspect_data["sentiment_score"] < -0.1]

                brand_summary[aspect] = {
                    "avg_score": round(aspect_data["sentiment_score"].mean(), 3),
                    "mention_count": len(aspect_data),
                    "positive_count": len(pos),
                    "negative_count": len(neg),
                    "sample_positive": pos["sentence"].iloc[0] if len(pos) > 0 else "",
                    "sample_negative": neg["sentence"].iloc[0] if len(neg) > 0 else "",
                }

            summary[brand] = brand_summary

        return summary


def run_aspect_analysis(reviews_path: str, output_dir: str = "data/processed"):
    """Run the complete aspect-level analysis pipeline."""
    import os
    import json

    print("\n" + "=" * 60)
    print("🔬 ASPECT-LEVEL SENTIMENT ANALYSIS")
    print("=" * 60)

    reviews_df = pd.read_csv(reviews_path)
    analyzer = AspectAnalyzer()

    # Run analysis
    aspects_df = analyzer.analyze_all_reviews(reviews_df)

    if not aspects_df.empty:
        # Brand × Aspect matrix
        matrix = analyzer.get_brand_aspect_matrix(aspects_df)
        print("\n  📊 Brand × Aspect Sentiment Matrix:")
        print(matrix.to_string())

        # Detailed summary
        summary = analyzer.get_aspect_summary(aspects_df)

        # Save results
        os.makedirs(output_dir, exist_ok=True)
        aspects_df.to_csv(f"{output_dir}/aspect_sentiments.csv", index=False)
        matrix.to_csv(f"{output_dir}/aspect_matrix.csv")

        with open(f"{output_dir}/aspect_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n  💾 Aspect analysis saved to {output_dir}/")

    print("=" * 60)
    return aspects_df


if __name__ == "__main__":
    run_aspect_analysis("data/processed/reviews.csv")
