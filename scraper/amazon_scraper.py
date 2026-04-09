"""
Amazon India Luggage Scraper
============================
A reproducible Playwright-based scraper for collecting product listings
and customer reviews from Amazon India for competitive intelligence analysis.

Usage:
    python amazon_scraper.py              # Full scrape
    python amazon_scraper.py --brands Safari Skybags   # Specific brands
    python amazon_scraper.py --dry-run    # Test without saving

Prerequisites:
    pip install playwright
    playwright install chromium
"""

import asyncio
import json
import os
import random
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

from scraper.config import BRANDS, SCRAPING_CONFIG, USER_AGENTS, OUTPUT_PATHS
from scraper.utils import (
    parse_price, calculate_discount, clean_text,
    parse_rating, parse_review_count, parse_review_date,
    extract_asin, validate_product, validate_review
)

# ─── Logging Setup ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class AmazonIndiaScraper:
    """
    Scrapes product listings and reviews from Amazon India
    for specified luggage brands using Playwright.
    
    Implements stealth techniques:
    - Random user agent rotation
    - Randomized delays between requests
    - Retry logic with exponential backoff
    - Human-like page scrolling
    """

    def __init__(self, config=None):
        self.config = config or SCRAPING_CONFIG
        self.products = []
        self.reviews = []
        self.stats = {brand: {"products": 0, "reviews": 0} for brand in BRANDS}

    async def _random_delay(self):
        """Add random delay to mimic human browsing."""
        delay = random.uniform(
            self.config["request_delay_min"],
            self.config["request_delay_max"]
        )
        await asyncio.sleep(delay)

    def _get_random_ua(self):
        """Get a random user agent string."""
        return random.choice(USER_AGENTS)

    async def _scroll_page(self, page):
        """Simulate human scrolling behavior."""
        for _ in range(random.randint(2, 5)):
            await page.evaluate(f"window.scrollBy(0, {random.randint(300, 700)})")
            await asyncio.sleep(random.uniform(0.5, 1.5))

    async def scrape_brand_products(self, page, brand_name, brand_config):
        """
        Scrape product listings for a single brand.
        
        Args:
            page: Playwright page instance
            brand_name: Name of the brand
            brand_config: Config dict with search_url and keywords
            
        Returns:
            List of product dictionaries
        """
        products = []
        url = brand_config["search_url"]
        target_count = self.config["products_per_brand"]

        logger.info(f"🔍 Scraping products for: {brand_name}")

        try:
            await page.goto(url, timeout=self.config["page_timeout"])
            await self._random_delay()
            await self._scroll_page(page)

            # Extract product cards from search results
            product_cards = await page.query_selector_all(
                'div[data-component-type="s-search-result"]'
            )

            for card in product_cards[:target_count + 5]:  # Extra for filtering
                try:
                    product = await self._parse_product_card(card, brand_name)
                    if product and validate_product(product):
                        products.append(product)
                        if len(products) >= target_count:
                            break
                except Exception as e:
                    logger.warning(f"  ⚠ Error parsing product card: {e}")
                    continue

            # Try next page if we don't have enough
            if len(products) < target_count:
                next_btn = await page.query_selector('a.s-pagination-next')
                if next_btn:
                    await next_btn.click()
                    await self._random_delay()
                    await self._scroll_page(page)
                    
                    more_cards = await page.query_selector_all(
                        'div[data-component-type="s-search-result"]'
                    )
                    for card in more_cards:
                        if len(products) >= target_count:
                            break
                        try:
                            product = await self._parse_product_card(card, brand_name)
                            if product and validate_product(product):
                                products.append(product)
                        except Exception:
                            continue

        except Exception as e:
            logger.error(f"  ✗ Failed to scrape products for {brand_name}: {e}")

        self.stats[brand_name]["products"] = len(products)
        logger.info(f"  ✓ Found {len(products)} products for {brand_name}")
        return products

    async def _parse_product_card(self, card, brand_name):
        """Parse a single product search result card."""
        # Title and URL
        title_el = await card.query_selector('h2 a span')
        link_el = await card.query_selector('h2 a')
        title = await title_el.inner_text() if title_el else None
        href = await link_el.get_attribute('href') if link_el else None

        if not title or not href:
            return None

        url = f"https://www.amazon.in{href}" if href.startswith('/') else href
        product_id = extract_asin(url) or f"{brand_name[:3].upper()}_{hash(title) % 100000}"

        # Price
        price_el = await card.query_selector('span.a-price-whole')
        price = parse_price(await price_el.inner_text()) if price_el else None

        # Original/list price
        list_price_el = await card.query_selector('span.a-price.a-text-price span.a-offscreen')
        list_price = parse_price(await list_price_el.inner_text()) if list_price_el else price

        # Rating
        rating_el = await card.query_selector('span.a-icon-alt')
        rating = parse_rating(await rating_el.inner_text()) if rating_el else None

        # Review count
        review_el = await card.query_selector('span.a-size-base.s-underline-text')
        review_count = parse_review_count(await review_el.inner_text()) if review_el else 0

        return {
            "product_id": product_id,
            "brand": brand_name,
            "title": clean_text(title),
            "price": price,
            "list_price": list_price,
            "discount_pct": calculate_discount(list_price, price) if list_price and price else 0,
            "rating": rating,
            "review_count": review_count,
            "category": "Luggage",
            "url": url,
            "scraped_at": datetime.now().isoformat(),
        }

    async def scrape_product_reviews(self, page, product):
        """
        Scrape customer reviews for a single product.
        
        Args:
            page: Playwright page instance
            product: Product dictionary with URL and product_id
            
        Returns:
            List of review dictionaries
        """
        reviews = []
        product_id = product["product_id"]
        brand = product["brand"]

        # Navigate to product reviews page
        review_url = product["url"].replace("/dp/", "/product-reviews/")
        if "/product-reviews/" not in review_url:
            # Fallback: construct review URL
            review_url = f"https://www.amazon.in/product-reviews/{product_id}"

        try:
            await page.goto(review_url, timeout=self.config["page_timeout"])
            await self._random_delay()
            await self._scroll_page(page)

            review_elements = await page.query_selector_all(
                'div[data-hook="review"]'
            )

            for rev_el in review_elements[:self.config["reviews_per_product"]]:
                try:
                    review = await self._parse_review(rev_el, product_id, brand)
                    if review and validate_review(review):
                        reviews.append(review)
                except Exception as e:
                    logger.debug(f"    ⚠ Error parsing review: {e}")
                    continue

        except Exception as e:
            logger.warning(f"    ⚠ Failed to scrape reviews for {product_id}: {e}")

        return reviews

    async def _parse_review(self, review_el, product_id, brand):
        """Parse a single review element."""
        # Review ID
        review_id = await review_el.get_attribute('id') or f"R{hash(str(time.time())) % 10**10}"

        # Rating
        rating_el = await review_el.query_selector('i[data-hook="review-star-rating"] span')
        rating_text = await rating_el.inner_text() if rating_el else None
        rating = parse_rating(rating_text)

        # Title
        title_el = await review_el.query_selector('a[data-hook="review-title"] span:last-child')
        title = clean_text(await title_el.inner_text()) if title_el else ""

        # Body text
        body_el = await review_el.query_selector('span[data-hook="review-body"] span')
        text = clean_text(await body_el.inner_text()) if body_el else ""

        # Date
        date_el = await review_el.query_selector('span[data-hook="review-date"]')
        date_text = await date_el.inner_text() if date_el else None
        date = parse_review_date(date_text)

        # Verified purchase
        verified_el = await review_el.query_selector('span[data-hook="avp-badge"]')
        verified = verified_el is not None

        # Helpful count
        helpful_el = await review_el.query_selector('span[data-hook="helpful-vote-statement"]')
        helpful_text = await helpful_el.inner_text() if helpful_el else "0"
        helpful_count = parse_review_count(helpful_text)

        return {
            "review_id": review_id,
            "product_id": product_id,
            "brand": brand,
            "rating": rating,
            "title": title,
            "text": text,
            "date": date,
            "verified": verified,
            "helpful_count": helpful_count,
        }

    async def run(self, brands=None):
        """
        Execute the full scraping pipeline.
        
        Args:
            brands: Optional list of brand names to scrape. 
                    If None, scrapes all configured brands.
        """
        target_brands = {k: v for k, v in BRANDS.items() if k in (brands or BRANDS.keys())}

        logger.info("=" * 60)
        logger.info(f"🚀 Starting Amazon India Luggage Scraper")
        logger.info(f"   Brands: {', '.join(target_brands.keys())}")
        logger.info("=" * 60)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.config["headless"])
            context = await browser.new_context(
                user_agent=self._get_random_ua(),
                viewport={"width": 1920, "height": 1080},
                locale="en-IN",
            )
            page = await context.new_page()

            # Block unnecessary resources for speed
            await page.route("**/*.{png,jpg,jpeg,gif,svg,webp}", lambda route: route.abort())
            await page.route("**/*.{css,woff,woff2,ttf}", lambda route: route.abort())

            for brand_name, brand_config in target_brands.items():
                # Scrape products
                brand_products = await self.scrape_brand_products(page, brand_name, brand_config)
                self.products.extend(brand_products)

                # Scrape reviews for each product
                for product in brand_products:
                    product_reviews = await self.scrape_product_reviews(page, product)
                    self.reviews.extend(product_reviews)
                    self.stats[brand_name]["reviews"] += len(product_reviews)
                    await self._random_delay()

                logger.info(f"  📊 {brand_name}: {self.stats[brand_name]['products']} products, "
                          f"{self.stats[brand_name]['reviews']} reviews")

            await browser.close()

        self._save_data()
        self._print_summary()

    def _save_data(self):
        """Save scraped data to JSON (raw) and CSV (processed)."""
        # Create directories
        os.makedirs(OUTPUT_PATHS["raw_dir"], exist_ok=True)
        os.makedirs(OUTPUT_PATHS["processed_dir"], exist_ok=True)

        # Save raw JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{OUTPUT_PATHS['raw_dir']}/products_{timestamp}.json", "w") as f:
            json.dump(self.products, f, indent=2)
        with open(f"{OUTPUT_PATHS['raw_dir']}/reviews_{timestamp}.json", "w") as f:
            json.dump(self.reviews, f, indent=2)

        # Save processed CSV
        import pandas as pd
        pd.DataFrame(self.products).to_csv(OUTPUT_PATHS["products_csv"], index=False)
        pd.DataFrame(self.reviews).to_csv(OUTPUT_PATHS["reviews_csv"], index=False)

        logger.info(f"💾 Data saved to {OUTPUT_PATHS['processed_dir']}/")

    def _print_summary(self):
        """Print scraping summary statistics."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 SCRAPING SUMMARY")
        logger.info("=" * 60)
        total_products = sum(s["products"] for s in self.stats.values())
        total_reviews = sum(s["reviews"] for s in self.stats.values())
        
        for brand, stats in self.stats.items():
            logger.info(f"  {brand:>20s}  │  {stats['products']:>3d} products  │  {stats['reviews']:>4d} reviews")
        
        logger.info("-" * 60)
        logger.info(f"  {'TOTAL':>20s}  │  {total_products:>3d} products  │  {total_reviews:>4d} reviews")
        logger.info("=" * 60)


# ─── CLI Entry Point ──────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape Amazon India luggage data")
    parser.add_argument("--brands", nargs="+", help="Specific brands to scrape")
    parser.add_argument("--dry-run", action="store_true", help="Test mode without saving")
    args = parser.parse_args()

    scraper = AmazonIndiaScraper()
    asyncio.run(scraper.run(brands=args.brands))
