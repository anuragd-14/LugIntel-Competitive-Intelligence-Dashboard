# Sentiment Analysis Methodology

## Overview

This document describes the sentiment analysis methodology used in the Competitive Intelligence Dashboard for analyzing customer reviews of luggage brands on Amazon India.

## 1. Dual-Model Sentiment Scoring

We employ a **dual-model approach** combining two established NLP sentiment analyzers to improve robustness:

### 1.1 VADER (Valence Aware Dictionary for Sentiment Reasoning)
- **Type:** Rule-based, lexicon-driven
- **Strengths:** Optimized for social media/review text; handles negations, degree modifiers, emojis, and punctuation emphasis
- **Output:** Compound score (-1 to +1), plus positive/negative/neutral component scores
- **Why chosen:** VADER is specifically designed for short-form opinion text like reviews and doesn't require training data

### 1.2 TextBlob
- **Type:** Pattern-based using averaged perceptron
- **Strengths:** Provides polarity and subjectivity scores; good at handling longer, well-structured text
- **Output:** Polarity (-1 to +1) and Subjectivity (0 to 1)
- **Why chosen:** Acts as a secondary validation layer; different algorithmic approach catches cases VADER misses

### 1.3 Combined Score
The final sentiment score is a **weighted combination**:

```
Combined Score = 0.65 × VADER_compound + 0.35 × TextBlob_polarity
```

**Rationale for weighting:** VADER receives higher weight (65%) because it was specifically designed for review/social media text and handles informal language patterns better. TextBlob at 35% serves as a stabilizing secondary signal.

### 1.4 Classification Thresholds
| Label | Combined Score Range |
|-------|---------------------|
| Positive | ≥ +0.15 |
| Neutral | -0.15 to +0.15 |
| Negative | ≤ -0.15 |

## 2. Theme Extraction via TF-IDF

Review themes are extracted using **Term Frequency-Inverse Document Frequency (TF-IDF)** analysis:

1. Reviews are split into positive and negative subsets per brand
2. Custom stop words are applied (luggage-domain-specific: "bag", "luggage", "trolley", "product", etc.)
3. TF-IDF vectorization with unigrams and bigrams (ngram_range=(1,2))
4. Top keywords are ranked by aggregate TF-IDF score across all documents in each subset
5. The top 8 keywords per sentiment polarity per brand are reported

## 3. Aspect-Level Sentiment Analysis (BONUS)

### 3.1 Aspect Detection
We use curated **keyword dictionaries** for 8 luggage-specific aspects:

| Aspect | Keywords (sample) |
|--------|-------------------|
| Wheels | wheel, spinner, caster, rotation, swivel, 360 |
| Handle | handle, grip, telescopic, retractable |
| Material | material, polycarbonate, hardside, nylon, ABS |
| Zipper | zipper, zip, closure, chain, YKK |
| Size & Capacity | capacity, spacious, compartment, pocket, expandable |
| Durability | durable, sturdy, break, crack, damage, flimsy |
| Weight | lightweight, heavy, weighs, portable |
| Lock | lock, TSA, combination, security |

### 3.2 Methodology
1. Review text is split into sentences
2. Each sentence is scanned against all aspect dictionaries
3. When an aspect keyword is found, VADER sentiment is computed on that sentence
4. Results are aggregated to product and brand level, producing an **Aspect × Brand sentiment matrix**

### 3.3 Limitations
- Keyword-based approach may miss implicit references ("the bag is so big inside" → Size aspect)
- Sentence-level sentiment may attribute wrong polarity when multiple aspects are in one sentence
- Sarcasm and highly contextual language are not well captured

## 4. Anomaly Detection (BONUS)

Four types of anomalies are detected:

### 4.1 Rating-Sentiment Mismatch
- Products with ≥4.0★ star rating but negative average NLP sentiment (<0.05)
- Indicates potential disconnect between star ratings and actual review content

### 4.2 Suspicious Rating Distribution
- Products where >75% of reviews are either 5★ or 1★ with very few middle ratings
- This bimodal "J-curve" or "U-shape" pattern may indicate review manipulation

### 4.3 Hidden Durability Issues
- Products with ≥3.8★ rating where ≥20% of reviews contain durability complaint keywords
- Keywords: "broke", "broken", "crack", "damage", "fell apart", "flimsy", etc.

### 4.4 Price-Quality Outliers
- Uses IQR (Interquartile Range) method on price-per-star ratios
- Identifies products that are statistically overpriced or underpriced relative to their rating

## 5. Review Trust Signal Analysis (BONUS)

### 5.1 Signals Analyzed
| Signal | Method | Weight |
|--------|--------|--------|
| Text Similarity | TF-IDF cosine similarity between reviews | 30% |
| Distribution | Rating distribution naturalness analysis | 20% |
| Verified Purchases | Percentage of verified purchase reviews | 25% |
| Review Quality | Length variance, detail level analysis | 25% |

### 5.2 Trust Score Formula
```
Trust Score = 0.30 × Similarity_Score + 0.20 × Distribution_Score 
            + 0.25 × Verified_Score + 0.25 × Length_Quality_Score
```
- Score range: 0-100
- Classification: High (≥70), Medium (50-70), Low (<50)

## 6. Value-for-Money Analysis (BONUS)

### 6.1 Price Band Definitions
| Band | Price Range |
|------|-------------|
| Budget | ₹0 - ₹2,500 |
| Mid-Range | ₹2,500 - ₹5,000 |
| Premium | ₹5,000+ |

### 6.2 VFM Score Formula
```
VFM Score = (0.5 × Normalized_Sentiment + 0.5 × Normalized_Rating) / (Normalized_Price + 0.1)
```
- Higher score = better value for money
- Normalization: Min-Max scaling to [0, 1] across all products

## 7. Agent Insights (BONUS)

Five categories of insights are auto-generated using statistical analysis:

1. **Hidden Quality Leader:** Brand with highest sentiment-to-price ratio
2. **Discount Trap:** Correlation between discount depth and sentiment
3. **Durability Dark Horse:** Best aspect-level durability sentiment at non-premium price
4. **Review Authenticity Alert:** Products/brands with lowest composite trust scores
5. **Market Gap:** Price bands with high demand-to-supply ratios

Each insight includes supporting data evidence, confidence level, and actionable recommendations.

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Sentiment Scoring | VADER | 3.3.2 |
| Secondary Scoring | TextBlob | 0.17+ |
| Theme Extraction | scikit-learn TF-IDF | 1.3+ |
| Data Processing | Pandas | 2.1+ |
| Visualization | Plotly | 5.18+ |
| Dashboard | Streamlit | 1.32+ |
