# Data Dictionary

## Products Dataset (`products.csv`)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `product_id` | string | Unique Amazon ASIN identifier | B4FA36A41 |
| `brand` | string | Brand name | Safari |
| `title` | string | Full product title from listing | Safari Pentagon Hardside... |
| `price` | float | Current selling price in INR (₹) | 2499.0 |
| `list_price` | float | MRP / list price in INR (₹) | 3899.0 |
| `discount_pct` | float | Discount percentage | 35.9 |
| `rating` | float | Average star rating (1.0-5.0) | 4.2 |
| `review_count` | int | Total number of customer reviews | 156 |
| `category` | string | Luggage sub-category | Cabin / Medium / Large / Set |
| `size` | string | Size specification | 55cm / 66cm / 76cm |
| `url` | string | Amazon India product URL | https://www.amazon.in/dp/... |

## Reviews Dataset (`reviews.csv`)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `review_id` | string | Unique review identifier | R4BN7K2M1A... |
| `product_id` | string | Associated product ASIN | B4FA36A41 |
| `brand` | string | Brand name of the product | Safari |
| `rating` | int | Star rating given (1-5) | 4 |
| `title` | string | Review title/headline | Great product! |
| `text` | string | Full review body text | Excellent luggage... |
| `date` | date | Review submission date (YYYY-MM-DD) | 2024-06-15 |
| `verified` | bool | Whether purchase is verified | True |
| `helpful_count` | int | Number of helpful votes | 5 |

## Analyzed Reviews (`reviews_analyzed.csv`)

All columns from `reviews.csv` plus:

| Column | Type | Description |
|--------|------|-------------|
| `full_text` | string | Concatenated title + text |
| `vader_compound` | float | VADER compound score (-1 to +1) |
| `vader_pos` | float | VADER positive component |
| `vader_neg` | float | VADER negative component |
| `vader_neu` | float | VADER neutral component |
| `textblob_polarity` | float | TextBlob polarity (-1 to +1) |
| `textblob_subjectivity` | float | TextBlob subjectivity (0 to 1) |
| `combined_score` | float | Weighted: 0.65*VADER + 0.35*TextBlob |
| `sentiment_label` | string | Positive / Neutral / Negative |

## Brand Sentiment (`brand_sentiment.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `brand` | string | Brand name (index) |
| `avg_sentiment` | float | Mean combined sentiment score |
| `median_sentiment` | float | Median combined score |
| `std_sentiment` | float | Standard deviation |
| `review_count` | int | Total reviews analyzed |
| `positive_pct` | float | % of positive reviews |
| `neutral_pct` | float | % of neutral reviews |
| `negative_pct` | float | % of negative reviews |

## Aspect Sentiments (`aspect_sentiments.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `review_id` | string | Source review ID |
| `product_id` | string | Product ASIN |
| `brand` | string | Brand name |
| `aspect` | string | Detected aspect (Wheels, Handle, etc.) |
| `keyword_matched` | string | Specific keyword that triggered detection |
| `sentence` | string | Sentence containing the aspect mention |
| `sentiment_score` | float | VADER sentiment of that sentence |

## Trust Scores (`trust_scores.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | string | Product ASIN |
| `brand` | string | Brand name |
| `title` | string | Product title |
| `review_count` | int | Reviews analyzed |
| `similarity_score` | float | Text uniqueness (0-100) |
| `distribution_score` | float | Rating distribution naturalness (0-100) |
| `verified_score` | float | Verified purchase ratio (0-100) |
| `length_quality_score` | float | Review text quality (0-100) |
| `trust_score` | float | Composite trust score (0-100) |
| `trust_level` | string | High / Medium / Low |

## Value for Money (`value_for_money.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | string | Product ASIN |
| `brand` | string | Brand name |
| `title` | string | Product title |
| `price` | float | Selling price |
| `price_band` | string | Budget / Mid-Range / Premium |
| `avg_sentiment` | float | Average review sentiment |
| `vfm_score` | float | Value-for-money score |
| `vfm_rank` | int | VFM ranking (1 = best) |
| `vfm_label` | string | Excellent / Good / Below Average |
