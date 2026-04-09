"""
Sentiment Analysis Engine
=========================
Dual-approach sentiment analysis using VADER and TextBlob.
Generates overall sentiment scores, theme extraction via TF-IDF,
and per-brand sentiment aggregations.

Methodology:
    1. VADER (Valence Aware Dictionary for Sentiment Reasoning) provides
       a rule-based sentiment score optimized for social media / review text.
    2. TextBlob provides a secondary polarity score using a pattern-based approach.
    3. The final score is a weighted combination: 0.65 * VADER + 0.35 * TextBlob.
    4. Theme extraction uses TF-IDF on positive vs negative review subsets.
"""

import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import warnings
warnings.filterwarnings("ignore")


class SentimentAnalyzer:
    """
    Multi-method sentiment analyzer for product reviews.
    
    Combines VADER and TextBlob scores with configurable weighting
    to produce robust sentiment classifications.
    """

    # Weight distribution between models
    VADER_WEIGHT = 0.65
    TEXTBLOB_WEIGHT = 0.35

    # Sentiment thresholds (on combined score -1 to +1)
    POS_THRESHOLD = 0.15
    NEG_THRESHOLD = -0.15

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def analyze_text(self, text: str) -> dict:
        """
        Analyze a single text and return sentiment scores.
        
        Returns:
            dict with keys: vader_compound, textblob_polarity, 
                           combined_score, sentiment_label
        """
        if not text or not isinstance(text, str) or len(text.strip()) < 3:
            return {
                "vader_compound": 0.0,
                "vader_pos": 0.0,
                "vader_neg": 0.0,
                "vader_neu": 0.0,
                "textblob_polarity": 0.0,
                "textblob_subjectivity": 0.0,
                "combined_score": 0.0,
                "sentiment_label": "Neutral",
            }

        # VADER analysis
        vader_scores = self.vader.polarity_scores(text)

        # TextBlob analysis
        blob = TextBlob(text)
        tb_polarity = blob.sentiment.polarity
        tb_subjectivity = blob.sentiment.subjectivity

        # Combined weighted score
        combined = (
            self.VADER_WEIGHT * vader_scores["compound"]
            + self.TEXTBLOB_WEIGHT * tb_polarity
        )

        # Classification
        if combined >= self.POS_THRESHOLD:
            label = "Positive"
        elif combined <= self.NEG_THRESHOLD:
            label = "Negative"
        else:
            label = "Neutral"

        return {
            "vader_compound": round(vader_scores["compound"], 4),
            "vader_pos": round(vader_scores["pos"], 4),
            "vader_neg": round(vader_scores["neg"], 4),
            "vader_neu": round(vader_scores["neu"], 4),
            "textblob_polarity": round(tb_polarity, 4),
            "textblob_subjectivity": round(tb_subjectivity, 4),
            "combined_score": round(combined, 4),
            "sentiment_label": label,
        }

    def analyze_reviews(self, reviews_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze sentiment for all reviews in a DataFrame.
        
        Args:
            reviews_df: DataFrame with 'text' and 'title' columns
            
        Returns:
            DataFrame with added sentiment columns
        """
        print("  🔍 Running VADER + TextBlob sentiment analysis...")
        
        # Combine title and text for analysis
        reviews_df = reviews_df.copy()
        reviews_df["full_text"] = (
            reviews_df["title"].fillna("") + ". " + reviews_df["text"].fillna("")
        )

        # Analyze each review
        sentiment_results = reviews_df["full_text"].apply(self.analyze_text)
        sentiment_df = pd.DataFrame(sentiment_results.tolist())

        # Merge results
        for col in sentiment_df.columns:
            reviews_df[col] = sentiment_df[col].values

        # Print summary
        label_counts = reviews_df["sentiment_label"].value_counts()
        print(f"    ✓ Positive: {label_counts.get('Positive', 0)} | "
              f"Neutral: {label_counts.get('Neutral', 0)} | "
              f"Negative: {label_counts.get('Negative', 0)}")

        return reviews_df

    def get_brand_sentiment(self, reviews_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate sentiment scores by brand.
        
        Returns:
            DataFrame indexed by brand with avg scores and label distributions.
        """
        brand_agg = reviews_df.groupby("brand").agg(
            avg_sentiment=("combined_score", "mean"),
            median_sentiment=("combined_score", "median"),
            std_sentiment=("combined_score", "std"),
            avg_vader=("vader_compound", "mean"),
            avg_textblob=("textblob_polarity", "mean"),
            review_count=("review_id", "count"),
            positive_pct=("sentiment_label", lambda x: (x == "Positive").mean() * 100),
            neutral_pct=("sentiment_label", lambda x: (x == "Neutral").mean() * 100),
            negative_pct=("sentiment_label", lambda x: (x == "Negative").mean() * 100),
        ).round(4)

        return brand_agg.sort_values("avg_sentiment", ascending=False)

    def extract_themes(self, reviews_df: pd.DataFrame, n_themes: int = 8) -> dict:
        """
        Extract key positive and negative themes per brand using TF-IDF.
        
        Args:
            reviews_df: DataFrame with sentiment labels and text
            n_themes: Number of themes per category per brand
            
        Returns:
            dict: {brand: {"positive_themes": [...], "negative_themes": [...]}}
        """
        print("  📝 Extracting review themes via TF-IDF...")

        # Custom stop words for luggage context
        custom_stop = {
            "bag", "luggage", "suitcase", "trolley", "product", "buy", "bought",
            "purchase", "amazon", "delivery", "delivered", "item", "order",
            "ordered", "received", "use", "used", "using", "would", "one",
            "also", "really", "much", "get", "got", "even", "like", "just",
            "good", "great", "nice", "best", "well", "bad", "worst", "poor",
            "brand", "star", "stars", "review", "recommend", "recommended",
            "money", "price", "worth", "value", "trip", "travel", "time",
            "first", "two", "day", "days", "week", "month",
        }

        themes = {}

        for brand in reviews_df["brand"].unique():
            brand_reviews = reviews_df[reviews_df["brand"] == brand]

            pos_texts = brand_reviews[brand_reviews["sentiment_label"] == "Positive"]["full_text"].tolist()
            neg_texts = brand_reviews[brand_reviews["sentiment_label"] == "Negative"]["full_text"].tolist()

            pos_themes = self._extract_tfidf_keywords(pos_texts, custom_stop, n_themes)
            neg_themes = self._extract_tfidf_keywords(neg_texts, custom_stop, n_themes)

            themes[brand] = {
                "positive_themes": pos_themes,
                "negative_themes": neg_themes,
            }

        return themes

    def _extract_tfidf_keywords(self, texts: list, stop_words: set, n: int) -> list:
        """Extract top-n TF-IDF keywords from a collection of texts."""
        if not texts or len(texts) < 2:
            return []

        try:
            # Clean texts
            cleaned = [re.sub(r'[^a-zA-Z\s]', '', t.lower()) for t in texts]

            vectorizer = TfidfVectorizer(
                max_features=200,
                stop_words=list(stop_words) + ["english"],
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.85,
            )
            tfidf_matrix = vectorizer.fit_transform(cleaned)
            feature_names = vectorizer.get_feature_names_out()

            # Sum TF-IDF scores across all documents
            scores = tfidf_matrix.sum(axis=0).A1
            top_indices = scores.argsort()[-n:][::-1]

            return [
                {"keyword": feature_names[i], "score": round(float(scores[i]), 3)}
                for i in top_indices
            ]
        except Exception:
            return []


def run_sentiment_analysis(reviews_path: str, output_dir: str = "data/processed"):
    """
    Run the full sentiment analysis pipeline.
    
    Args:
        reviews_path: Path to reviews CSV
        output_dir: Directory to save results
    """
    import os
    import json

    print("\n" + "=" * 60)
    print("🧠 SENTIMENT ANALYSIS PIPELINE")
    print("=" * 60)

    # Load reviews
    reviews_df = pd.read_csv(reviews_path)
    print(f"  📥 Loaded {len(reviews_df)} reviews from {reviews_path}")

    # Initialize analyzer
    analyzer = SentimentAnalyzer()

    # Run sentiment analysis
    analyzed_df = analyzer.analyze_reviews(reviews_df)

    # Get brand-level aggregation
    brand_sentiment = analyzer.get_brand_sentiment(analyzed_df)
    print("\n  📊 Brand Sentiment Ranking:")
    for brand, row in brand_sentiment.iterrows():
        emoji = "🟢" if row["avg_sentiment"] > 0.15 else ("🟡" if row["avg_sentiment"] > -0.05 else "🔴")
        print(f"    {emoji} {brand:>20s}  │  Score: {row['avg_sentiment']:+.3f}  │  "
              f"Pos: {row['positive_pct']:.0f}%  Neg: {row['negative_pct']:.0f}%")

    # Extract themes
    themes = analyzer.extract_themes(analyzed_df)

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    analyzed_df.to_csv(f"{output_dir}/reviews_analyzed.csv", index=False)
    brand_sentiment.to_csv(f"{output_dir}/brand_sentiment.csv")
    
    with open(f"{output_dir}/themes.json", "w") as f:
        json.dump(themes, f, indent=2)

    print(f"\n  💾 Results saved to {output_dir}/")
    print("=" * 60)

    return analyzed_df, brand_sentiment, themes


if __name__ == "__main__":
    run_sentiment_analysis("data/processed/reviews.csv")
