"""
Analysis Pipeline Runner
=========================
Runs the complete analysis pipeline end-to-end:
1. Sentiment Analysis (VADER + TextBlob)
2. Aspect-Level Sentiment (BONUS)
3. Anomaly Detection (BONUS)
4. Trust Signals (BONUS)
5. Value-for-Money Analysis (BONUS)
6. Agent Insights Generation (BONUS)

Usage:
    python run_analysis.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    data_dir = "data/processed"
    products_path = f"{data_dir}/products.csv"
    reviews_path = f"{data_dir}/reviews.csv"

    print("\n" + "█" * 60)
    print("     COMPETITIVE INTELLIGENCE ANALYSIS PIPELINE")
    print("     Luggage Brands on Amazon India")
    print("█" * 60)

    # ── Step 1: Sentiment Analysis ─────────────────────────────
    from analysis.sentiment import run_sentiment_analysis
    analyzed_df, brand_sentiment, themes = run_sentiment_analysis(reviews_path, data_dir)

    # ── Step 2: Aspect-Level Sentiment ─────────────────────────
    from analysis.aspect_analysis import run_aspect_analysis
    aspects_df = run_aspect_analysis(reviews_path, data_dir)

    # ── Step 3: Anomaly Detection ──────────────────────────────
    from analysis.anomaly_detection import run_anomaly_detection
    anomalies = run_anomaly_detection(
        products_path, f"{data_dir}/reviews_analyzed.csv", data_dir
    )

    # ── Step 4: Trust Signals ──────────────────────────────────
    from analysis.trust_signals import run_trust_analysis
    trust_df = run_trust_analysis(products_path, reviews_path, data_dir)

    # ── Step 5: Value-for-Money ────────────────────────────────
    from analysis.value_for_money import run_value_analysis
    vfm_df = run_value_analysis(
        products_path, f"{data_dir}/reviews_analyzed.csv", data_dir
    )

    # ── Step 6: Agent Insights ─────────────────────────────────
    from analysis.agent_insights import run_agent_insights
    insights = run_agent_insights(data_dir, data_dir)

    # ── Summary ────────────────────────────────────────────────
    print("\n" + "█" * 60)
    print("     ✅ ANALYSIS PIPELINE COMPLETE")
    print("█" * 60)
    print(f"  📁 All results saved in: {data_dir}/")
    print(f"  📄 Files generated:")
    for f in sorted(os.listdir(data_dir)):
        size = os.path.getsize(f"{data_dir}/{f}") / 1024
        print(f"      • {f} ({size:.1f} KB)")
    print("█" * 60)


if __name__ == "__main__":
    main()
