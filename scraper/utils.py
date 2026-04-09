"""
Utility functions for scraping and data cleaning.
Handles price parsing, text cleaning, and data validation.
"""

import re
import html
from datetime import datetime
from typing import Optional


def parse_price(price_str: str) -> Optional[float]:
    """
    Parse Indian Rupee price strings into float values.
    Handles formats like '₹2,499.00', 'Rs. 3,999', '₹ 1,299' etc.
    """
    if not price_str:
        return None
    # Remove currency symbols, spaces, and commas
    cleaned = re.sub(r'[₹,Rs.\s]', '', str(price_str))
    try:
        return float(cleaned)
    except ValueError:
        return None


def calculate_discount(list_price: float, selling_price: float) -> float:
    """Calculate discount percentage from list price and selling price."""
    if not list_price or list_price <= 0 or not selling_price:
        return 0.0
    discount = ((list_price - selling_price) / list_price) * 100
    return round(max(0, min(100, discount)), 1)


def clean_text(text: str) -> str:
    """
    Clean review/product text by removing HTML entities, 
    extra whitespace, and special characters.
    """
    if not text:
        return ""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_rating(rating_str: str) -> Optional[float]:
    """
    Parse Amazon rating strings like '4.2 out of 5 stars' into float.
    """
    if not rating_str:
        return None
    match = re.search(r'(\d+\.?\d*)', str(rating_str))
    if match:
        rating = float(match.group(1))
        if 0 <= rating <= 5:
            return rating
    return None


def parse_review_count(count_str: str) -> int:
    """
    Parse review count strings like '1,234 ratings' or '456 reviews'.
    """
    if not count_str:
        return 0
    cleaned = re.sub(r'[,\s]', '', str(count_str))
    match = re.search(r'(\d+)', cleaned)
    return int(match.group(1)) if match else 0


def parse_review_date(date_str: str) -> Optional[str]:
    """
    Parse Amazon India review date formats.
    Returns ISO format date string.
    """
    if not date_str:
        return None
    
    # Common formats: "Reviewed in India on 15 January 2024"
    date_str = re.sub(r'Reviewed in \w+ on ', '', str(date_str))
    
    formats = [
        "%d %B %Y",
        "%B %d, %Y",
        "%d %b %Y",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def extract_asin(url: str) -> Optional[str]:
    """Extract ASIN (product ID) from Amazon URL."""
    if not url:
        return None
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    match = re.search(r'/product/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    return None


def validate_product(product: dict) -> bool:
    """Validate that a product record has minimum required fields."""
    required = ['product_id', 'brand', 'title', 'price']
    return all(product.get(field) for field in required)


def validate_review(review: dict) -> bool:
    """Validate that a review record has minimum required fields."""
    required = ['review_id', 'product_id', 'rating', 'text']
    return all(review.get(field) for field in required)
