"""
Configuration for Amazon India luggage brand scraping.
Defines target brands, search URLs, and scraping parameters.
"""

# ─── Brand Configuration ───────────────────────────────────────────
BRANDS = {
    "Safari": {
        "search_url": "https://www.amazon.in/s?k=Safari+luggage+trolley+bag",
        "keywords": ["Safari"],
    },
    "Skybags": {
        "search_url": "https://www.amazon.in/s?k=Skybags+luggage+trolley+bag",
        "keywords": ["Skybags", "SKYBAGS"],
    },
    "American Tourister": {
        "search_url": "https://www.amazon.in/s?k=American+Tourister+luggage+trolley+bag",
        "keywords": ["American Tourister"],
    },
    "VIP": {
        "search_url": "https://www.amazon.in/s?k=VIP+luggage+trolley+bag",
        "keywords": ["VIP", "V.I.P"],
    },
    "Aristocrat": {
        "search_url": "https://www.amazon.in/s?k=Aristocrat+luggage+trolley+bag",
        "keywords": ["Aristocrat"],
    },
    "Nasher Miles": {
        "search_url": "https://www.amazon.in/s?k=Nasher+Miles+luggage+trolley+bag",
        "keywords": ["Nasher Miles"],
    },
}

# ─── Scraping Parameters ──────────────────────────────────────────
SCRAPING_CONFIG = {
    "products_per_brand": 15,       # Target number of products per brand
    "reviews_per_product": 10,      # Target reviews per product
    "min_reviews_per_brand": 50,    # Minimum total reviews per brand
    "request_delay_min": 2.0,       # Minimum delay between requests (seconds)
    "request_delay_max": 5.0,       # Maximum delay between requests (seconds)
    "max_retries": 3,               # Maximum retries per page
    "page_timeout": 30000,          # Page load timeout (ms)
    "headless": True,               # Run browser in headless mode
}

# ─── User Agent Rotation ──────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

# ─── Output Paths ─────────────────────────────────────────────────
OUTPUT_PATHS = {
    "raw_dir": "data/raw",
    "processed_dir": "data/processed",
    "products_csv": "data/processed/products.csv",
    "reviews_csv": "data/processed/reviews.csv",
}
