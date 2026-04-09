"""
Competitive Intelligence Dashboard
====================================
Main Streamlit application for the Amazon India Luggage 
Competitive Intelligence Dashboard.

Run with:
    streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
from pathlib import Path

# ─── Page Configuration ──────────────────────────────────────
st.set_page_config(
    page_title="Luggage Intelligence Dashboard | Amazon India",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Resolve project root ─────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "processed"
ASSETS_DIR = Path(__file__).parent / "assets"
sys.path.insert(0, str(ROOT))

# ─── Load custom CSS ──────────────────────────────────────────
css_path = ASSETS_DIR / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# ─── Data Loading Functions (cached) ─────────────────────────
@st.cache_data(ttl=3600)
def load_products():
    return pd.read_csv(DATA_DIR / "products.csv")

@st.cache_data(ttl=3600)
def load_reviews():
    try:
        return pd.read_csv(DATA_DIR / "reviews_analyzed.csv")
    except FileNotFoundError:
        return pd.read_csv(DATA_DIR / "reviews.csv")

@st.cache_data(ttl=3600)
def load_brand_sentiment():
    try:
        return pd.read_csv(DATA_DIR / "brand_sentiment.csv", index_col=0)
    except FileNotFoundError:
        return None

@st.cache_data(ttl=3600)
def load_themes():
    try:
        with open(DATA_DIR / "themes.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@st.cache_data(ttl=3600)
def load_aspect_matrix():
    try:
        return pd.read_csv(DATA_DIR / "aspect_matrix.csv", index_col=0)
    except FileNotFoundError:
        return None

@st.cache_data(ttl=3600)
def load_aspect_sentiments():
    try:
        return pd.read_csv(DATA_DIR / "aspect_sentiments.csv")
    except FileNotFoundError:
        return None

@st.cache_data(ttl=3600)
def load_trust_scores():
    try:
        return pd.read_csv(DATA_DIR / "trust_scores.csv")
    except FileNotFoundError:
        return None

@st.cache_data(ttl=3600)
def load_vfm():
    try:
        return pd.read_csv(DATA_DIR / "value_for_money.csv")
    except FileNotFoundError:
        return None

@st.cache_data(ttl=3600)
def load_anomalies():
    try:
        with open(DATA_DIR / "anomalies.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@st.cache_data(ttl=3600)
def load_insights():
    try:
        with open(DATA_DIR / "agent_insights.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@st.cache_data(ttl=3600)
def load_price_band_analysis():
    try:
        return pd.read_csv(DATA_DIR / "price_band_analysis.csv")
    except FileNotFoundError:
        return None


# ─── Load all data ────────────────────────────────────────────
products = load_products()
reviews = load_reviews()
brand_sentiment = load_brand_sentiment()
themes = load_themes()
aspect_matrix = load_aspect_matrix()
aspect_sentiments = load_aspect_sentiments()
trust_scores = load_trust_scores()
vfm_data = load_vfm()
anomalies = load_anomalies()
insights = load_insights()
price_bands = load_price_band_analysis()

# ─── Store in session state for page access ───────────────────
st.session_state["products"] = products
st.session_state["reviews"] = reviews
st.session_state["brand_sentiment"] = brand_sentiment
st.session_state["themes"] = themes
st.session_state["aspect_matrix"] = aspect_matrix
st.session_state["aspect_sentiments"] = aspect_sentiments
st.session_state["trust_scores"] = trust_scores
st.session_state["vfm_data"] = vfm_data
st.session_state["anomalies"] = anomalies
st.session_state["insights"] = insights
st.session_state["price_bands"] = price_bands

# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """<div style='text-align:center; padding: 0.8rem 0 0.4rem;'>
            <span style='font-size:2.4rem;'>🧳</span><br>
            <span style='font-family:Outfit,sans-serif; font-weight:800; font-size:1.5rem;
                         background:linear-gradient(135deg,#22d3ee,#a78bfa);
                         -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                         letter-spacing:-0.02em;'>LugIntel</span><br>
            <span style='font-size:0.72rem; color:#64748b; letter-spacing:0.06em;
                         text-transform:uppercase; font-weight:500;'>
                Competitive Intelligence</span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.divider()

    # Navigation
    page = st.radio(
        "Navigate",
        options=[
            "📊 Dashboard Overview",
            "⚔️ Brand Comparison",
            "🔍 Product Drilldown",
            "🤖 Agent Insights",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.divider()

    # Quick stats
    st.markdown("### 📈 Quick Stats")
    st.metric("Brands Tracked", len(products["brand"].unique()))
    st.metric("Total Products", len(products))
    st.metric("Total Reviews", len(reviews))

    if brand_sentiment is not None:
        avg_sent = brand_sentiment["avg_sentiment"].mean()
        st.metric("Avg Sentiment", f"{avg_sent:+.3f}")

    st.divider()
    st.markdown(
        "<div class='footer-text'>Moonshot AI Internship Assignment<br>"
        "NLP: VADER + TextBlob · Charts: Plotly</div>",
        unsafe_allow_html=True,
    )

# ─── Page Router ──────────────────────────────────────────────
if page == "📊 Dashboard Overview":
    from dashboard.pages.overview import render_overview
    render_overview(products, reviews, brand_sentiment, themes)

elif page == "⚔️ Brand Comparison":
    from dashboard.pages.brand_comparison import render_brand_comparison
    render_brand_comparison(products, reviews, brand_sentiment, themes,
                           aspect_matrix, aspect_sentiments, vfm_data, price_bands)

elif page == "🔍 Product Drilldown":
    from dashboard.pages.product_drilldown import render_product_drilldown
    render_product_drilldown(products, reviews, trust_scores, anomalies,
                            aspect_sentiments, themes)

elif page == "🤖 Agent Insights":
    from dashboard.pages.agent_insights import render_agent_insights
    render_agent_insights(insights, anomalies, vfm_data, trust_scores,
                         products, reviews, brand_sentiment)
