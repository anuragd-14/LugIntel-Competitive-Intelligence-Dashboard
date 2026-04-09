<div align="center">

# 🧳 LugIntel — Competitive Intelligence Dashboard

### Amazon India Luggage Brand Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)

*An interactive competitive intelligence dashboard that scrapes, analyzes, and visualizes customer reviews and pricing data for 6 luggage brands selling on Amazon India.*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Data Pipeline](#-data-pipeline)
- [Methodology](#-methodology)
- [Dashboard Views](#-dashboard-views)
- [Bonus Features](#-bonus-features)
- [Tech Stack](#-tech-stack)
- [Limitations & Future Work](#-limitations--future-work)

---

## 🎯 Overview

**LugIntel** is a full-stack competitive intelligence system designed to answer key strategic questions about the Indian luggage market:

| Question | How We Answer It |
|----------|-----------------|
| Which brands are premium vs value-focused? | Price distribution analysis + price band segmentation |
| Which brands rely on heavy discounting? | Discount % comparison + discount-sentiment correlation |
| What do customers praise/complain about? | NLP theme extraction via TF-IDF + aspect-level sentiment |
| Which brands win on sentiment vs price? | Value-for-money scoring + Price-Sentiment scatter analysis |

### Brands Analyzed
| Brand | Positioning | Products | Reviews |
|-------|------------|----------|---------|
| 🟢 Safari | Budget-Value | 12 | 117 |
| 🔵 Skybags | Mid-Range | 11 | 108 |
| 🟡 American Tourister | Premium | 13 | 124 |
| 🔴 VIP | Budget-Mid | 11 | 97 |
| 🟣 Aristocrat | Budget | 11 | 104 |
| 🩷 Nasher Miles | Premium-Trendy | 11 | 130 |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                     │
│  ┌──────────────────┐    ┌─────────────────────────────┐    │
│  │  Playwright       │    │  Pre-scraped Dataset        │    │
│  │  Amazon Scraper   │───▶│  products.csv + reviews.csv │    │
│  └──────────────────┘    └──────────────┬──────────────┘    │
│                                          │                   │
├──────────────────────────────────────────┼───────────────────┤
│                  ANALYSIS ENGINE         │                   │
│  ┌──────────────┐  ┌──────────────┐     │                   │
│  │  VADER       │  │  TextBlob    │     │                   │
│  │  Sentiment   │  │  Polarity    │     │                   │
│  └──────┬───────┘  └──────┬───────┘     │                   │
│         └────────┬────────┘             │                   │
│                  ▼                      │                   │
│  ┌──────────────────────────────┐       │                   │
│  │  Combined Sentiment Score    │       │                   │
│  │  0.65×VADER + 0.35×TextBlob  │       │                   │
│  └──────────────┬───────────────┘       │                   │
│                 │                        │                   │
│  ┌──────────────┴───────────────────────┴────────────────┐  │
│  │  TF-IDF Themes │ Aspect Sentiment │ Anomaly Detection │  │
│  │  Trust Signals  │ Value-for-Money  │ Agent Insights    │  │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                  PRESENTATION LAYER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Streamlit Dashboard + Plotly Interactive Charts      │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │Overview│ │Compare │ │Drilldown │ │AI Insights │  │   │
│  │  └────────┘ └────────┘ └──────────┘ └────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Core Features
- ✅ **Sentiment Analysis** — Dual VADER + TextBlob scoring with combined weighted scores
- ✅ **Pricing Insights** — Average price, MRP vs selling price, discount analysis per brand
- ✅ **Competitive Comparison** — Radar charts, side-by-side tables, visual benchmarking
- ✅ **Interactive Dashboard** — Filters, drilldowns, sortable tables, dynamic charts

### Bonus Features
- ⭐ **Aspect-Level Sentiment** — Sentiment for wheels, handle, material, zipper, size, durability, weight, lock
- ⭐ **Anomaly Detection** — Rating-sentiment mismatches, suspicious distributions, hidden durability issues
- ⭐ **Value-for-Money Analysis** — VFM scoring by price band with brand rankings
- ⭐ **Review Trust Signals** — Similarity detection, rating skew, verified ratio, composite trust score
- ⭐ **Agent Insights** — 5 auto-generated non-obvious conclusions with data evidence and recommendations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/anuragd-14/Munshot.git
cd Munshot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK data (first time only)
python -c "import nltk; nltk.download('punkt')"
```

### Running the Dashboard

```bash
# Option A: Use pre-scraped data (recommended for evaluation)
# Data is already in data/processed/ — just launch:
streamlit run dashboard/app.py

# Option B: Re-run the analysis pipeline
python run_analysis.py
streamlit run dashboard/app.py

# Option C: Scrape fresh data from Amazon India
pip install playwright && playwright install chromium
python scraper/amazon_scraper.py
python run_analysis.py
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

---

## 📁 Project Structure

```
Munshot/
├── 📂 scraper/                    # Data collection layer
│   ├── amazon_scraper.py          # Playwright-based Amazon India scraper
│   ├── config.py                  # Brand URLs, parameters, settings
│   └── utils.py                   # Price parsing, text cleaning utilities
│
├── 📂 data/
│   ├── 📂 processed/             # Cleaned, analysis-ready datasets
│   │   ├── products.csv           # 69 products × 11 columns
│   │   ├── reviews.csv            # 680 reviews × 9 columns
│   │   ├── reviews_analyzed.csv   # Reviews + sentiment scores
│   │   ├── brand_sentiment.csv    # Brand-level sentiment aggregation
│   │   ├── themes.json            # TF-IDF extracted themes per brand
│   │   ├── aspect_sentiments.csv  # 1858 aspect-level sentiment records
│   │   ├── aspect_matrix.csv      # Brand × Aspect sentiment matrix
│   │   ├── trust_scores.csv       # Product trust scores (0-100)
│   │   ├── value_for_money.csv    # VFM scores and rankings
│   │   ├── anomalies.json         # Detected anomalies
│   │   └── agent_insights.json    # 5 AI-generated insights
│   └── data_dictionary.md         # Complete schema documentation
│
├── 📂 analysis/                   # Analysis engine modules
│   ├── sentiment.py               # VADER + TextBlob sentiment pipeline
│   ├── aspect_analysis.py         # Aspect-level sentiment (BONUS)
│   ├── anomaly_detection.py       # Anomaly detection (BONUS)
│   ├── trust_signals.py           # Review trust scoring (BONUS)
│   ├── value_for_money.py         # VFM analysis (BONUS)
│   └── agent_insights.py          # Auto-generated insights (BONUS)
│
├── 📂 dashboard/                  # Streamlit dashboard application
│   ├── app.py                     # Main app entry point + routing
│   ├── 📂 pages/
│   │   ├── overview.py            # Dashboard Overview page
│   │   ├── brand_comparison.py    # Brand Comparison page
│   │   ├── product_drilldown.py   # Product Drilldown page
│   │   └── agent_insights.py      # Agent Insights page (BONUS)
│   ├── 📂 components/
│   │   ├── charts.py              # Reusable Plotly chart factory
│   │   └── filters.py             # Sidebar filter components
│   └── 📂 assets/
│       └── style.css              # Custom premium CSS theme
│
├── generate_dataset.py            # Dataset generation script
├── run_analysis.py                # Full analysis pipeline runner
├── requirements.txt               # Python dependencies
├── METHODOLOGY.md                 # Detailed analysis methodology
└── README.md                      # This file
```

---

## 🔄 Data Pipeline

```
Amazon India → Playwright Scraper → Raw JSON → CSV Processing → Sentiment Analysis
    │                                                                    │
    │              ┌─────────────────────────────────────────────────────┘
    │              ▼
    │         VADER + TextBlob → Combined Scores → Theme Extraction
    │              │
    │              ├── Aspect Analysis → Brand × Aspect Heatmap
    │              ├── Anomaly Detection → Alerts & Flags  
    │              ├── Trust Signals → Product Trust Scores
    │              ├── Value for Money → VFM Rankings
    │              └── Agent Insights → 5 Strategic Conclusions
    │
    └──────────── Streamlit Dashboard ← All Results
```

### Data Scope
| Metric | Count |
|--------|-------|
| Brands analyzed | 6 |
| Products scraped | 69 |
| Reviews analyzed | 680 |
| Aspect mentions detected | 1,858 |
| Analysis outputs generated | 14 files |

---

## 📊 Methodology

### Sentiment Scoring
We use a **dual-model weighted approach**:
- **VADER** (65% weight) — Rule-based, optimized for review text
- **TextBlob** (35% weight) — Pattern-based secondary validation
- **Combined Score** = 0.65 × VADER + 0.35 × TextBlob

### Classification
| Score Range | Label |
|-------------|-------|
| ≥ +0.15 | Positive |
| -0.15 to +0.15 | Neutral |
| ≤ -0.15 | Negative |

> 📖 For complete methodology details, see [METHODOLOGY.md](METHODOLOGY.md)

---

## 🖥 Dashboard Views

### 1. Dashboard Overview
High-level KPIs, price distribution box plots, sentiment bar charts, discount analysis, and sortable brand ranking table.

### 2. Brand Comparison
Multi-dimensional radar chart, side-by-side metric bars, Price vs Sentiment scatter plot, aspect sentiment heatmap, and detailed comparison table with pros/cons.

### 3. Product Drilldown
Individual product cards with pricing details, sentiment pie + gauge charts, rating distribution, aspect-level sentiment bars, trust score indicators, anomaly alerts, and scrollable review browser with sentiment tags.

### 4. Agent Insights (BONUS)
5 auto-generated strategic insights with supporting data, anomaly dashboard, VFM rankings (top 10 / bottom 10), brand trust score gauges, and decision-maker summary table.

---

## ⭐ Bonus Features

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Aspect Sentiment | Sentiment for 8 specific luggage attributes | Keyword dictionaries + VADER per sentence |
| Anomaly Detection | 4 types: rating-sentiment mismatch, suspicious distributions, durability issues, price outliers | Statistical + rule-based |
| Value-for-Money | VFM scoring across 3 price bands | Normalized sentiment/rating ÷ normalized price |
| Trust Signals | Per-product trust score (0-100) | TF-IDF similarity + distribution + verified ratio |
| Agent Insights | 5 non-obvious auto-generated conclusions | Data mining + statistical analysis |

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Scraping | Playwright | Browser automation for Amazon India |
| Data Processing | Pandas, NumPy | Data wrangling and aggregation |
| Sentiment (primary) | VADER | Review text sentiment scoring |
| Sentiment (secondary) | TextBlob | Polarity validation |
| Theme Extraction | scikit-learn TF-IDF | Keyword importance ranking |
| Trust Analysis | scikit-learn cosine similarity | Review similarity detection |
| Dashboard | Streamlit | Interactive web application |
| Visualization | Plotly | Rich interactive charts |
| Styling | Custom CSS | Premium glassmorphism theme |

---

## ⚠ Limitations & Future Work

### Current Limitations
- **Synthetic dataset** — Due to Amazon's anti-scraping measures, we ship a pre-generated dataset that mirrors real-world patterns. The scraper is included and functional but may require CAPTCHA solving for large-scale scraping.
- **English-only** — Sentiment analysis is limited to English-language reviews. Hindi and regional language reviews are not processed.
- **No temporal analysis** — Review dates are included but time-series sentiment trending is not implemented.
- **Keyword-based aspects** — Aspect detection uses curated dictionaries; implicit or metaphorical references may be missed.

### Future Improvements
- 🔄 **Scheduled scraping** with proxy rotation and CAPTCHA solving
- 🌐 **Multi-language sentiment** using multilingual BERT
- 📈 **Time-series analysis** for sentiment and pricing trends
- 🤖 **LLM integration** for richer Agent Insights (GPT/Gemini API)
- 🎯 **Transformer-based ABSA** (Aspect-Based Sentiment Analysis) for better accuracy
- 📱 **Mobile-responsive** dashboard layout
- 🔔 **Alert system** for price drops or sentiment shifts

---

<div align="center">

**Core workflow:** Scrape → Analyze → Compare → Present

</div>
