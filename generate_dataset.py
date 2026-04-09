"""
Dataset Generator for Amazon India Luggage Brands
==================================================
Generates a realistic pre-scraped dataset for the competitive intelligence dashboard.
This mimics real Amazon India data patterns for 6 luggage brands with
realistic pricing, ratings, reviews, and sentiment distributions.

The generated data reflects actual market patterns:
- American Tourister & Nasher Miles sit at premium price points
- Safari & Aristocrat are value/budget players
- Skybags & VIP occupy the mid-range
- Review sentiments follow realistic distributions with brand-specific tendencies

Usage:
    python generate_dataset.py
"""

import csv
import hashlib
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Seed for reproducibility
random.seed(42)

# ─── Brand Profiles ──────────────────────────────────────────────
# Each brand has realistic pricing ranges, typical ratings, and review sentiment tendencies
BRAND_PROFILES = {
    "Safari": {
        "price_range": (1299, 4999),
        "list_price_markup": (1.15, 1.55),  # Discount tendency
        "avg_rating": 3.9,
        "rating_std": 0.4,
        "sentiment_bias": 0.05,  # Slightly positive
        "products": [
            {"name": "Safari Pentagon Hardside Small Cabin Luggage", "cat": "Cabin", "size": "55cm"},
            {"name": "Safari Thorium Sharp Anti-Scratch Trolley Bag", "cat": "Medium", "size": "66cm"},
            {"name": "Safari Regloss Antiscratch Suitcase", "cat": "Large", "size": "76cm"},
            {"name": "Safari Crypto 4W Spinner Trolley Bag", "cat": "Cabin", "size": "55cm"},
            {"name": "Safari Ray Polycarbonate Hardsided Cabin Luggage", "cat": "Cabin", "size": "53cm"},
            {"name": "Safari Haze 8 Wheels Trolley Bag", "cat": "Medium", "size": "65cm"},
            {"name": "Safari Ozone Softside Spinner Suitcase", "cat": "Large", "size": "77cm"},
            {"name": "Safari Flo Secure 4W Trolley Bag", "cat": "Cabin", "size": "55cm"},
            {"name": "Safari Zen Polypropylene Hardsided Trolley", "cat": "Medium", "size": "66cm"},
            {"name": "Safari Axis 4 Wheel Trolley Bag Set", "cat": "Set", "size": "55+66+76cm"},
            {"name": "Safari Pentagon 4W Spinner Medium", "cat": "Medium", "size": "67cm"},
            {"name": "Safari Thorium Printed Hardside Cabin", "cat": "Cabin", "size": "55cm"},
        ],
        "strengths": ["affordable price", "good value", "lightweight", "decent space"],
        "weaknesses": ["wheel quality", "handle durability", "zip quality", "scratch marks"],
    },
    "Skybags": {
        "price_range": (1999, 6499),
        "list_price_markup": (1.20, 1.50),
        "avg_rating": 4.0,
        "rating_std": 0.35,
        "sentiment_bias": 0.10,
        "products": [
            {"name": "Skybags Neo Strolly Cabin Luggage", "cat": "Cabin", "size": "55cm"},
            {"name": "Skybags Trooper Polycarbonate Hardsided Suitcase", "cat": "Medium", "size": "65cm"},
            {"name": "Skybags Cube 4W Spinner Large", "cat": "Large", "size": "75cm"},
            {"name": "Skybags Zoom Ultra Trolley Bag", "cat": "Cabin", "size": "55cm"},
            {"name": "Skybags Stream Polycarbonate Hardcase", "cat": "Medium", "size": "67cm"},
            {"name": "Skybags Beach 4 Wheel Trolley Bag", "cat": "Cabin", "size": "55cm"},
            {"name": "Skybags Sonic Strolly Hardcase Luggage", "cat": "Large", "size": "78cm"},
            {"name": "Skybags Ramp Cabin Polycarbonate Spinner", "cat": "Cabin", "size": "55cm"},
            {"name": "Skybags Trick 4W Strolly Medium", "cat": "Medium", "size": "66cm"},
            {"name": "Skybags Majestic Softsided Trolley Set", "cat": "Set", "size": "55+66cm"},
            {"name": "Skybags Flashy Polycarbonate Cabin", "cat": "Cabin", "size": "55cm"},
        ],
        "strengths": ["stylish design", "color options", "sturdy build", "spacious"],
        "weaknesses": ["slightly heavy", "price for quality", "zipper stiffness", "handle wobble"],
    },
    "American Tourister": {
        "price_range": (2999, 12999),
        "list_price_markup": (1.25, 1.65),
        "avg_rating": 4.2,
        "rating_std": 0.3,
        "sentiment_bias": 0.18,
        "products": [
            {"name": "American Tourister Ivy Polypropylene Hardside Cabin", "cat": "Cabin", "size": "55cm"},
            {"name": "American Tourister Liftoff Spinner Medium", "cat": "Medium", "size": "68cm"},
            {"name": "American Tourister Stratos Polycarbonate Hardshell", "cat": "Large", "size": "77cm"},
            {"name": "American Tourister Instagon Spinner Trolley Bag", "cat": "Cabin", "size": "55cm"},
            {"name": "American Tourister Kamiliant Zakk Spinner", "cat": "Medium", "size": "68cm"},
            {"name": "American Tourister Splash Voyage Hardside", "cat": "Cabin", "size": "55cm"},
            {"name": "American Tourister Cascade Spinner Large", "cat": "Large", "size": "76cm"},
            {"name": "American Tourister Speedair Cabin 4W", "cat": "Cabin", "size": "55cm"},
            {"name": "American Tourister Jamaica Polypropylene Medium", "cat": "Medium", "size": "66cm"},
            {"name": "American Tourister Mighty Maze Spinner", "cat": "Cabin", "size": "55cm"},
            {"name": "American Tourister Ga0 Armor Trolley Set", "cat": "Set", "size": "55+68cm"},
            {"name": "American Tourister Fornax Spinner Hard Body", "cat": "Large", "size": "77cm"},
            {"name": "American Tourister Linex Polypropylene Cabin", "cat": "Cabin", "size": "55cm"},
        ],
        "strengths": ["excellent build quality", "smooth wheels", "trusted brand", "premium finish", "TSA lock"],
        "weaknesses": ["premium pricing", "heavy weight", "limited color choices", "size runs small"],
    },
    "VIP": {
        "price_range": (1499, 5999),
        "list_price_markup": (1.18, 1.52),
        "avg_rating": 3.8,
        "rating_std": 0.45,
        "sentiment_bias": -0.02,
        "products": [
            {"name": "VIP Outline 4W Cabin Trolley Bag", "cat": "Cabin", "size": "55cm"},
            {"name": "VIP Zest Polycarbonate Hardside Medium", "cat": "Medium", "size": "66cm"},
            {"name": "VIP Xion Polycarbonate Hardshell Large", "cat": "Large", "size": "75cm"},
            {"name": "VIP Polaris Spinner Trolley Bag", "cat": "Cabin", "size": "55cm"},
            {"name": "VIP Rush Polypropylene Hardsided Spinner", "cat": "Medium", "size": "66cm"},
            {"name": "VIP Drift Softside Cabin Luggage", "cat": "Cabin", "size": "55cm"},
            {"name": "VIP Pioneer Spinner Medium", "cat": "Medium", "size": "67cm"},
            {"name": "VIP Zeal Polycarbonate Cabin 4W", "cat": "Cabin", "size": "55cm"},
            {"name": "VIP Experia Hardsided Large Trolley", "cat": "Large", "size": "76cm"},
            {"name": "VIP Track Polypropylene Spinner Set", "cat": "Set", "size": "55+66+76cm"},
            {"name": "VIP Tide Cabin Trolley Bag", "cat": "Cabin", "size": "55cm"},
        ],
        "strengths": ["heritage brand", "good warranty", "lightweight", "affordable"],
        "weaknesses": ["wheel breakage", "material quality", "outdated design", "zip problems"],
    },
    "Aristocrat": {
        "price_range": (1199, 3999),
        "list_price_markup": (1.20, 1.60),
        "avg_rating": 3.7,
        "rating_std": 0.5,
        "sentiment_bias": -0.05,
        "products": [
            {"name": "Aristocrat Aston Polycarbonate Cabin Trolley", "cat": "Cabin", "size": "55cm"},
            {"name": "Aristocrat Harbour Medium Trolley Bag", "cat": "Medium", "size": "65cm"},
            {"name": "Aristocrat Jude Polypropylene Large", "cat": "Large", "size": "75cm"},
            {"name": "Aristocrat Vigour Hardside Cabin 4W", "cat": "Cabin", "size": "55cm"},
            {"name": "Aristocrat Crystal Spinner Medium", "cat": "Medium", "size": "66cm"},
            {"name": "Aristocrat Air Pro Cabin Trolley", "cat": "Cabin", "size": "55cm"},
            {"name": "Aristocrat Flow Softside Spinner Medium", "cat": "Medium", "size": "66cm"},
            {"name": "Aristocrat Photon Strolly Large", "cat": "Large", "size": "76cm"},
            {"name": "Aristocrat Warrior Hardcase Cabin", "cat": "Cabin", "size": "55cm"},
            {"name": "Aristocrat Cargo Max Trolley Set", "cat": "Set", "size": "55+66cm"},
            {"name": "Aristocrat Spark Polycarbonate Cabin", "cat": "Cabin", "size": "55cm"},
        ],
        "strengths": ["most affordable", "basic functionality", "lightweight", "simple design"],
        "weaknesses": ["poor durability", "wheel quality", "cheap material feel", "handle issues", "zipper failure"],
    },
    "Nasher Miles": {
        "price_range": (2999, 8999),
        "list_price_markup": (1.30, 1.70),
        "avg_rating": 4.1,
        "rating_std": 0.35,
        "sentiment_bias": 0.15,
        "products": [
            {"name": "Nasher Miles Lombard Hard-Sided Cabin Luggage", "cat": "Cabin", "size": "55cm"},
            {"name": "Nasher Miles Wall Street Hard-Sided Medium", "cat": "Medium", "size": "65cm"},
            {"name": "Nasher Miles Times Square Hardside Large", "cat": "Large", "size": "75cm"},
            {"name": "Nasher Miles Fifth Avenue Polycarbonate Cabin", "cat": "Cabin", "size": "55cm"},
            {"name": "Nasher Miles Park Avenue Spinner Medium", "cat": "Medium", "size": "67cm"},
            {"name": "Nasher Miles Broadway Hardcase Large", "cat": "Large", "size": "76cm"},
            {"name": "Nasher Miles Oxford Cabin Trolley 4W", "cat": "Cabin", "size": "55cm"},
            {"name": "Nasher Miles Bond Street Polycarbonate Medium", "cat": "Medium", "size": "66cm"},
            {"name": "Nasher Miles Soho Hardside Cabin Spinner", "cat": "Cabin", "size": "55cm"},
            {"name": "Nasher Miles Central Park Trolley Set", "cat": "Set", "size": "55+66+76cm"},
            {"name": "Nasher Miles Hudson Polycarbonate Large", "cat": "Large", "size": "78cm"},
        ],
        "strengths": ["premium look", "smooth 360 wheels", "excellent material", "trendy colors", "TSA lock"],
        "weaknesses": ["expensive", "heavy weight", "limited availability", "premium pricing"],
    },
}

# ─── Review Templates ────────────────────────────────────────────
# Realistic review templates with varying complexity and linguistic patterns
POSITIVE_REVIEWS = [
    "Excellent {product_type}! {strength1} and {strength2}. Very happy with my purchase. The {aspect} is really impressive. Would definitely buy again from {brand}.",
    "Great quality for the price. {strength1}. Used it for my trip and it handled everything well. The {aspect} works smoothly. Highly recommend.",
    "I bought this for my recent vacation and it was perfect. {strength1} and the {aspect} is top notch. {brand} has done a great job with this one.",
    "Very satisfied! The build quality is good, {strength1}. Packing was easy due to the spacious compartments. The {aspect} is excellent.",
    "Love this luggage! {strength1} and {strength2}. Looks premium and feels sturdy. The {aspect} quality is really good for this price range.",
    "Good product, delivered on time. {strength1}. The {aspect} impressed me the most. Using it regularly now - no complaints so far!",
    "Worth every rupee! {strength1} and {strength2}. Took it on a 2-week trip and came back without any scratches. {brand} quality is reliable.",
    "This is my second purchase from {brand} and they never disappoint. {strength1}. The {aspect} is even better than my previous bag.",
    "Amazing product at this price point. {strength1}. The material feels durable and the {aspect} is very smooth. Recommended for frequent travelers.",
    "Perfect cabin luggage! Fits all airline requirements. {strength1}. {aspect} is of great quality. Will suggest to friends.",
    "Bought for my parents - they loved it! {strength1} and easy to maneuver. The {aspect} makes it very convenient to use.",
    "Five stars! {strength1}, {strength2}, and excellent {aspect}. What more can you ask for at this price?",
    "Very practical and well-designed. {strength1}. The interiors are well-organized with multiple pockets. {aspect} quality is commendable.",
    "Using for office travel and it's perfect. {strength1}. Compact yet spacious. The {aspect} deserves special mention.",
    "Premium feel without the premium price tag. {strength1} and {strength2}. Really impressed with the {aspect}.",
]

MIXED_REVIEWS = [
    "Decent product overall. {strength1} but {weakness1}. The {aspect} is okay, nothing extraordinary. Serves its purpose for the price.",
    "Good for the price but has some issues. {strength1}. However, {weakness1}. The {aspect} could be better. 3/5 would buy again.",
    "Average quality. {strength1} which is nice, but {weakness1}. Not bad for occasional trips but frequent travelers should consider spending more.",
    "It's okay. {strength1}. {weakness1} though. For this price range, I guess it's acceptable. The {aspect} is mediocre.",
    "Mixed feelings about this one. {strength1} is great but {weakness1} is disappointing. Would rate it average.",
    "Product looks good but {weakness1}. {strength1} saves it somewhat. Usable but don't expect premium quality at this price.",
    "Not bad, not great. {strength1}. But I noticed {weakness1} after a few uses. The {aspect} started fine but degraded.",
    "For the price it's acceptable. {strength1}. But {weakness1} is a concern. Would give it 3 stars honestly.",
]

NEGATIVE_REVIEWS = [
    "Disappointed with the quality. {weakness1} and {weakness2}. The {aspect} broke within the first trip. Don't waste your money.",
    "Very poor quality for the price. {weakness1}. The {aspect} stopped working after just 2 uses. Expected better from {brand}.",
    "Worst purchase ever. {weakness1} and {weakness2}. The bag looks nothing like the pictures. {aspect} is terrible.",
    "Not recommended. {weakness1}. Material feels cheap and the {aspect} is pathetic. Save your money and buy a better brand.",
    "{weakness1} - this was my experience right out of the box. Also {weakness2}. Returning this immediately.",
    "Used once and already falling apart. {weakness1} and the {aspect} is already showing problems. Very disappointed with {brand}.",
    "Received a damaged product. Apart from that, {weakness1}. The {aspect} quality is unacceptable at any price point.",
    "Terrible durability. {weakness1} after just one flight. The {aspect} cracked during handling. Never buying {brand} again.",
    "Cheap quality disguised with flashy looks. {weakness1}. The {aspect} gave way on my first trip. Waste of money.",
    "One star. {weakness1} and {weakness2}. The {aspect} doesn't work properly. Amazon should remove this product.",
]

ASPECT_WORDS = ["wheels", "handle", "zipper", "material", "lock", "compartments", "weight", "build quality"]


def generate_review_id():
    """Generate a realistic Amazon-style review ID."""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "R" + "".join(random.choices(chars, k=13))


def generate_asin(brand, idx):
    """Generate a realistic ASIN-like product ID."""
    seed_str = f"{brand}_{idx}"
    hash_hex = hashlib.md5(seed_str.encode()).hexdigest()[:9].upper()
    return "B" + hash_hex[:9]


def generate_price(brand_profile):
    """Generate a realistic price from brand profile."""
    low, high = brand_profile["price_range"]
    # Cluster prices at common price points
    base = random.randint(low, high)
    # Round to common endings: 99, 49, etc.
    endings = [99, 49, 99, 99, 0]
    base = (base // 100) * 100 + random.choice(endings)
    return max(low, min(high, base))


def generate_review_text(brand, profile, rating):
    """Generate a realistic review text based on rating."""
    aspect = random.choice(ASPECT_WORDS)
    
    if rating >= 4:
        template = random.choice(POSITIVE_REVIEWS)
        strength1 = random.choice(profile["strengths"]).capitalize()
        strength2 = random.choice([s for s in profile["strengths"] if s != strength1.lower()])
        text = template.format(
            brand=brand, product_type="luggage", aspect=aspect,
            strength1=strength1, strength2=strength2
        )
    elif rating == 3:
        template = random.choice(MIXED_REVIEWS)
        strength1 = random.choice(profile["strengths"]).capitalize()
        weakness1 = random.choice(profile["weaknesses"])
        text = template.format(
            brand=brand, aspect=aspect,
            strength1=strength1, weakness1=weakness1
        )
    else:
        template = random.choice(NEGATIVE_REVIEWS)
        weakness1 = random.choice(profile["weaknesses"]).capitalize()
        weakness2 = random.choice([w for w in profile["weaknesses"] if w != weakness1.lower()])
        text = template.format(
            brand=brand, aspect=aspect,
            weakness1=weakness1, weakness2=weakness2
        )
    
    return text


def generate_rating(avg_rating, std):
    """Generate a rating from a realistic distribution, favoring the brand's average."""
    # Use a weighted distribution that mimics Amazon's typical J-curve
    rating = round(random.gauss(avg_rating, std))
    return max(1, min(5, rating))


def generate_date():
    """Generate a random date within the last 12 months."""
    days_ago = random.randint(1, 365)
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def generate_review_title(rating):
    """Generate a short review title based on rating."""
    positive_titles = [
        "Great product!", "Excellent quality", "Worth the money",
        "Love it!", "Perfect for travel", "Highly recommended",
        "Best luggage ever", "Amazing value", "Super happy",
        "Fantastic purchase", "Must buy!", "Very satisfied",
    ]
    mixed_titles = [
        "Average product", "Okay for the price", "Could be better",
        "Decent but not great", "Not bad", "Mediocre quality",
        "So-so", "Expected more", "Fair product",
    ]
    negative_titles = [
        "Very disappointed", "Terrible quality", "Don't buy this",
        "Waste of money", "Poor quality", "Worst purchase",
        "Not recommended", "Broke quickly", "Cheap product",
        "Avoid this", "Huge regret",
    ]
    
    if rating >= 4:
        return random.choice(positive_titles)
    elif rating == 3:
        return random.choice(mixed_titles)
    else:
        return random.choice(negative_titles)


def main():
    """Generate the complete dataset."""
    output_dir = Path(__file__).parent / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_products = []
    all_reviews = []

    print("=" * 60)
    print("🏭 Generating Amazon India Luggage Dataset")
    print("=" * 60)

    for brand, profile in BRAND_PROFILES.items():
        print(f"\n📦 Generating data for {brand}...")
        
        brand_review_count = 0
        
        for idx, product_info in enumerate(profile["products"]):
            # Generate product
            asin = generate_asin(brand, idx)
            price = generate_price(profile)
            list_markup = random.uniform(*profile["list_price_markup"])
            list_price = round(price * list_markup / 100) * 100 + 99
            discount_pct = round(((list_price - price) / list_price) * 100, 1)
            
            # Rating (with some variance per product)
            product_avg_rating = profile["avg_rating"] + random.uniform(-0.3, 0.3)
            product_rating = round(max(2.5, min(5.0, product_avg_rating)), 1)
            
            # Reviews count per product (varied)
            num_reviews = random.randint(5, 15)
            total_review_count = random.randint(num_reviews * 3, num_reviews * 20)
            
            product = {
                "product_id": asin,
                "brand": brand,
                "title": product_info["name"],
                "price": price,
                "list_price": list_price,
                "discount_pct": discount_pct,
                "rating": product_rating,
                "review_count": total_review_count,
                "category": product_info["cat"],
                "size": product_info["size"],
                "url": f"https://www.amazon.in/dp/{asin}",
            }
            all_products.append(product)

            # Generate reviews for this product
            for _ in range(num_reviews):
                review_rating = generate_rating(product_avg_rating, profile["rating_std"])
                review_text = generate_review_text(brand, profile, review_rating)
                review_title = generate_review_title(review_rating)
                
                review = {
                    "review_id": generate_review_id(),
                    "product_id": asin,
                    "brand": brand,
                    "rating": review_rating,
                    "title": review_title,
                    "text": review_text,
                    "date": generate_date(),
                    "verified": random.random() > 0.15,  # ~85% verified
                    "helpful_count": random.choices(
                        [0, 0, 0, 1, 2, 3, 5, 8, 12, 25],
                        weights=[40, 20, 10, 10, 7, 5, 4, 2, 1, 1]
                    )[0],
                }
                all_reviews.append(review)
                brand_review_count += 1

        print(f"  ✓ {len(profile['products'])} products, {brand_review_count} reviews")

    # Save products CSV
    products_file = output_dir / "products.csv"
    with open(products_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_products[0].keys())
        writer.writeheader()
        writer.writerows(all_products)

    # Save reviews CSV
    reviews_file = output_dir / "reviews.csv"
    with open(reviews_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_reviews[0].keys())
        writer.writeheader()
        writer.writerows(all_reviews)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 DATASET SUMMARY")
    print("=" * 60)
    print(f"  Total Products: {len(all_products)}")
    print(f"  Total Reviews:  {len(all_reviews)}")
    print(f"  Brands:         {len(BRAND_PROFILES)}")
    
    for brand in BRAND_PROFILES:
        bp = [p for p in all_products if p["brand"] == brand]
        br = [r for r in all_reviews if r["brand"] == brand]
        print(f"    {brand:>20s}  │  {len(bp):>2d} products  │  {len(br):>3d} reviews")
    
    print(f"\n  📁 Products saved to: {products_file}")
    print(f"  📁 Reviews saved to:  {reviews_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
