# Comprehensive User Features Guide

## Overview

The Two Tower Model uses **55 comprehensive user features** that capture detailed user preferences across all major wine attributes. This provides rich user representations for highly personalized wine recommendations.

## Feature Categories (55 Total)

### 1. Basic User Statistics (8 features)
Fundamental rating behavior metrics:
- `rating_mean`: Average rating given by user (0-5)
- `rating_std`: Standard deviation of ratings (consistency measure)
- `rating_count`: Total number of ratings given
- `rating_min`: Minimum rating given
- `rating_max`: Maximum rating given
- `wines_tried`: Number of unique wines rated
- `avg_ratings_per_wine`: Average ratings per wine
- `coefficient_of_variation`: Rating std / rating mean (normalized consistency)

### 2. Wine Type Preferences (6 features)
Weighted average ratings for each wine type:
- `red_wine_preference`: Preference for red wines
- `white_wine_preference`: Preference for white wines
- `sparkling_wine_preference`: Preference for sparkling wines
- `rose_wine_preference`: Preference for rosé wines
- `dessert_wine_preference`: Preference for dessert wines
- `dessert_port_wine_preference`: Preference for dessert/port wines

### 3. Wine Attribute Preferences (25 features)

#### 3.1 ABV Preferences (3 features)
- `weighted_abv_preference`: ABV weighted by user ratings
- `avg_abv_tried`: Simple average of ABV values
- `high_vs_low_abv_preference`: High ABV rating - Low ABV rating

#### 3.2 Body Type Preferences (5 features)
- `very_light_bodied_preference`: Rating for very light-bodied wines
- `light_bodied_preference`: Rating for light-bodied wines
- `medium_bodied_preference`: Rating for medium-bodied wines
- `full_bodied_preference`: Rating for full-bodied wines
- `very_full_bodied_preference`: Rating for very full-bodied wines

#### 3.3 Acidity Preferences (3 features)
- `low_acidity_preference`: Rating for low acidity wines
- `medium_acidity_preference`: Rating for medium acidity wines
- `high_acidity_preference`: Rating for high acidity wines

#### 3.4 Country Preferences (5 features)
Top 5 countries by user's rating count:
- `country_1_preference` through `country_5_preference`
- Weighted average ratings for top 5 most-rated countries

#### 3.5 Grape Variety Preferences (5 features)
Top 5 grapes by user's rating count:
- `grape_1_preference` through `grape_5_preference`
- Weighted average ratings for top 5 most-rated primary grapes

#### 3.6 Wine Complexity Preferences (2 features)
- `complexity_preference`: Complex wine rating - Simple wine rating
- `avg_complexity_tried`: Average complexity level (1=Single, 2=Simple Blend, 3=Complex Blend)

#### 3.7 Wine Quality Indicators (2 features)
- `reserve_preference`: Reserve wine rating - Non-reserve wine rating
- `grand_preference`: Grand wine rating - Non-grand wine rating

### 4. Rating Behavior Patterns (8 features)
- `high_rating_proportion`: Proportion of 4-5 star ratings
- `low_rating_proportion`: Proportion of 1-2 star ratings
- `rating_entropy`: Entropy of rating distribution (diversity)
- `rating_1_proportion` through `rating_5_proportion`: Individual star proportions

### 5. Preference Diversity Metrics (4 features)
- `rating_range`: Max rating - Min rating
- `rating_variance`: Variance of user's ratings
- `unique_ratings_count`: Number of different rating values used
- `rating_skewness`: Skewness of rating distribution

### 6. Temporal Rating Patterns (4 features)
- `date_range_days`: Days between first and last rating
- `avg_days_between_ratings`: Average temporal spacing
- `rating_trend`: Linear trend in ratings over time
- `rating_frequency`: Ratings per day

## Input Format

### Comprehensive Features (Recommended)

```json
{
  "basic_features": {
    "rating_mean": 3.8,
    "rating_std": 0.95,
    "rating_count": 150,
    "rating_min": 1.0,
    "rating_max": 5.0,
    "wines_tried": 120,
    "avg_ratings_per_wine": 1.25,
    "coefficient_of_variation": 0.25
  },
  "wine_type_preferences": {
    "red_wine_preference": 4.2,
    "white_wine_preference": 3.5,
    "sparkling_wine_preference": 3.8,
    "rose_wine_preference": 3.3,
    "dessert_wine_preference": 0.0,
    "dessert_port_wine_preference": 0.0
  },
  "wine_attribute_preferences": {
    "abv_preferences": {
      "weighted_abv_preference": 13.5,
      "avg_abv_tried": 13.2,
      "high_vs_low_abv_preference": 0.3
    },
    "body_type_preferences": {
      "very_light_bodied_preference": 0.0,
      "light_bodied_preference": 3.2,
      "medium_bodied_preference": 3.8,
      "full_bodied_preference": 4.1,
      "very_full_bodied_preference": 3.9
    },
    "acidity_preferences": {
      "low_acidity_preference": 3.5,
      "medium_acidity_preference": 3.9,
      "high_acidity_preference": 3.6
    },
    "country_preferences": {
      "country_1_preference": 4.2,
      "country_2_preference": 3.8,
      "country_3_preference": 3.6,
      "country_4_preference": 3.4,
      "country_5_preference": 3.2
    },
    "grape_preferences": {
      "grape_1_preference": 4.3,
      "grape_2_preference": 4.0,
      "grape_3_preference": 3.7,
      "grape_4_preference": 3.5,
      "grape_5_preference": 3.4
    },
    "complexity_preferences": {
      "complexity_preference": 0.5,
      "avg_complexity_tried": 2.1
    },
    "quality_indicators": {
      "reserve_preference": 0.3,
      "grand_preference": 0.2
    }
  },
  "rating_patterns": {
    "high_rating_proportion": 0.65,
    "low_rating_proportion": 0.08,
    "rating_entropy": 1.25,
    "rating_1_proportion": 0.02,
    "rating_2_proportion": 0.06,
    "rating_3_proportion": 0.27,
    "rating_4_proportion": 0.45,
    "rating_5_proportion": 0.20
  },
  "diversity_metrics": {
    "rating_range": 4.0,
    "rating_variance": 0.9025,
    "unique_ratings_count": 5,
    "rating_skewness": -0.35
  },
  "temporal_patterns": {
    "date_range_days": 365,
    "avg_days_between_ratings": 2.43,
    "rating_trend": 0.001,
    "rating_frequency": 0.41
  }
}
```

### Legacy Simple Format (Backward Compatibility)

```json
{
  "type": "Red",
  "body": 4,
  "dryness": 3,
  "abv": 13.5
}
```

## API Usage

### Making Requests

```bash
# Using comprehensive features (recommended)
curl -X POST http://localhost:8080/wines \
  -H "Content-Type: application/json" \
  -d @user_features.json

# Using simple preferences (legacy)
curl -X POST http://localhost:8080/wines/legacy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Red",
    "body": 4,
    "dryness": 3,
    "abv": 13.5
  }'
```

### Response Format

```json
{
  "wines": ["wine_123", "wine_456", "wine_789"],
  "scores": {
    "wine_123": 0.95,
    "wine_456": 0.87,
    "wine_789": 0.82
  }
}
```

## Feature Calculation Notes

### Weighted Averages
All preference features use weighted averages where the weight is the user's rating:
```
weighted_avg = Σ(rating × attribute_value) / Σ(rating)
```

This ensures wines the user rated higher have more influence on their preferences.

### Difference Metrics
Preference difference metrics capture relative preferences:
- `high_vs_low_abv_preference = avg_rating_high_abv - avg_rating_low_abv`
- `complexity_preference = avg_rating_complex - avg_rating_simple`

Positive values indicate preference for the first category, negative for the second.

### Top-N Selection
Country and grape preferences use the user's top 5 by rating count:
1. Count ratings per country/grape for this user
2. Rank by count (most-rated first)
3. Take top 5
4. Calculate weighted average rating for each

## Benefits

### 1. Precision
- Captures nuanced preferences across all wine attributes
- Enables fine-grained recommendation matching
- Handles diverse user taste profiles

### 2. Personalization
- Rich user embeddings for better similarity matching
- Detailed preference profiles
- More relevant recommendations

### 3. Flexibility
- Supports both comprehensive and simple formats
- Gradual feature enrichment as users rate more wines
- Backward compatible with legacy systems

### 4. Interpretability
- Features are human-readable and meaningful
- Enables user profiling and analysis
- Facilitates debugging and model improvement

## Example: Feature Vector Format

When sent to the model, features are flattened into a 55-dimensional vector:

```python
[
  # Basic features (8)
  3.8, 0.95, 150, 1.0, 5.0, 120, 1.25, 0.25,
  
  # Wine type preferences (6)
  4.2, 3.5, 3.8, 3.3, 0.0, 0.0,
  
  # ABV preferences (3)
  13.5, 13.2, 0.3,
  
  # Body type preferences (5)
  0.0, 3.2, 3.8, 4.1, 3.9,
  
  # ... and so on for all 55 features
]
```

## Migration from Simple to Comprehensive

If you're currently using simple preferences, you can:

1. Continue using `/wines/legacy` endpoint
2. Gradually collect user rating data
3. Calculate comprehensive features offline
4. Switch to `/wines` endpoint with full features
5. Enjoy better recommendations!

## See Also

- `TWO_TOWER_MIGRATION.md`: Migration guide
- `schemas/user_schema.py`: Schema definitions
- `services/model_service.py`: Feature processing implementation
