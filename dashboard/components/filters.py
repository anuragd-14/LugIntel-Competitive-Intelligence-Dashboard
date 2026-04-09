"""
Filter components for the Streamlit dashboard sidebar.
Provides reusable filter widgets with consistent styling.
"""

import streamlit as st
import pandas as pd


def render_brand_filter(products_df: pd.DataFrame, key: str = "brand_filter") -> list:
    """Render a multi-select brand filter in the sidebar."""
    brands = sorted(products_df["brand"].unique().tolist())
    selected = st.multiselect(
        "🏷️ Select Brands",
        options=brands,
        default=brands,
        key=key,
        help="Choose one or more brands to include in the analysis",
    )
    return selected if selected else brands


def render_price_filter(products_df: pd.DataFrame, key: str = "price_filter") -> tuple:
    """Render a price range slider."""
    min_price = int(products_df["price"].min())
    max_price = int(products_df["price"].max())
    
    price_range = st.slider(
        "💰 Price Range (₹)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=100,
        key=key,
        format="₹%d",
    )
    return price_range


def render_rating_filter(key: str = "rating_filter") -> float:
    """Render a minimum rating filter."""
    min_rating = st.slider(
        "⭐ Minimum Rating",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.5,
        key=key,
    )
    return min_rating


def render_sentiment_filter(key: str = "sentiment_filter") -> list:
    """Render a sentiment category filter."""
    options = ["Positive", "Neutral", "Negative"]
    selected = st.multiselect(
        "😊 Sentiment Filter",
        options=options,
        default=options,
        key=key,
    )
    return selected if selected else options


def render_category_filter(products_df: pd.DataFrame, key: str = "category_filter") -> list:
    """Render a luggage category filter."""
    if "category" not in products_df.columns:
        return []
    
    categories = sorted(products_df["category"].unique().tolist())
    selected = st.multiselect(
        "🧳 Luggage Category",
        options=categories,
        default=categories,
        key=key,
    )
    return selected if selected else categories


def render_price_band_filter(key: str = "price_band_filter") -> list:
    """Render price band filter."""
    bands = ["Budget", "Mid-Range", "Premium"]
    selected = st.multiselect(
        "📊 Price Band",
        options=bands,
        default=bands,
        key=key,
    )
    return selected if selected else bands


def apply_filters(products_df, reviews_df=None, brands=None, price_range=None,
                  min_rating=None, categories=None):
    """Apply all selected filters to the dataframes."""
    filtered_products = products_df.copy()
    
    if brands:
        filtered_products = filtered_products[filtered_products["brand"].isin(brands)]
    
    if price_range:
        filtered_products = filtered_products[
            (filtered_products["price"] >= price_range[0]) &
            (filtered_products["price"] <= price_range[1])
        ]
    
    if min_rating and min_rating > 1.0:
        filtered_products = filtered_products[filtered_products["rating"] >= min_rating]
    
    if categories:
        if "category" in filtered_products.columns:
            filtered_products = filtered_products[filtered_products["category"].isin(categories)]
    
    filtered_reviews = None
    if reviews_df is not None:
        filtered_reviews = reviews_df[
            reviews_df["product_id"].isin(filtered_products["product_id"])
        ]
    
    return filtered_products, filtered_reviews
