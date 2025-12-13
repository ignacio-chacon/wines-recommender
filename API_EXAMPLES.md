# Flattened User Features API Examples

## Request Format

The API now accepts user features as a **flattened key:value JSON object** with 55 features.

## Example: Comprehensive User Features Request

```bash
curl -X POST http://localhost:8080/wines \
  -H "Content-Type: application/json" \
  -d '{
    "rating_mean": 3.8,
    "rating_std": 0.95,
    "rating_count": 150,
    "rating_min": 1.0,
    "rating_max": 5.0,
    "wines_tried": 120,
    "avg_ratings_per_wine": 1.25,
    "coefficient_of_variation": 0.25,
    "red_wine_preference": 4.2,
    "white_wine_preference": 3.5,
    "sparkling_wine_preference": 3.8,
    "rose_wine_preference": 3.3,
    "dessert_wine_preference": 0.0,
    "dessert_port_wine_preference": 0.0,
    "weighted_abv_preference": 13.5,
    "avg_abv_tried": 13.2,
    "high_vs_low_abv_preference": 0.3,
    "very_light_bodied_preference": 0.0,
    "light_bodied_preference": 3.2,
    "medium_bodied_preference": 3.8,
    "full_bodied_preference": 4.1,
    "very_full_bodied_preference": 3.9,
    "low_acidity_preference": 3.5,
    "medium_acidity_preference": 3.9,
    "high_acidity_preference": 3.6,
    "country_1_preference": 4.2,
    "country_2_preference": 3.8,
    "country_3_preference": 3.6,
    "country_4_preference": 3.4,
    "country_5_preference": 3.2,
    "grape_1_preference": 4.3,
    "grape_2_preference": 4.0,
    "grape_3_preference": 3.7,
    "grape_4_preference": 3.5,
    "grape_5_preference": 3.4,
    "complexity_preference": 0.5,
    "avg_complexity_tried": 2.1,
    "reserve_preference": 0.3,
    "grand_preference": 0.2,
    "high_rating_proportion": 0.65,
    "low_rating_proportion": 0.08,
    "rating_entropy": 1.25,
    "rating_1_proportion": 0.02,
    "rating_2_proportion": 0.06,
    "rating_3_proportion": 0.27,
    "rating_4_proportion": 0.45,
    "rating_5_proportion": 0.20,
    "rating_range": 4.0,
    "rating_variance": 0.9025,
    "unique_ratings_count": 5,
    "rating_skewness": -0.35,
    "date_range_days": 365,
    "avg_days_between_ratings": 2.43,
    "rating_trend": 0.001,
    "rating_frequency": 0.41
  }'
```

## Example: Legacy Simple Preferences (Still Supported)

```bash
curl -X POST http://localhost:8080/wines \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Red",
    "body": 4,
    "dryness": 3,
    "abv": 13.5
  }'
```

## Feature Order (for reference)

The 55 features are processed in this order:

### 1. Basic Features (8)
1. rating_mean
2. rating_std
3. rating_count
4. rating_min
5. rating_max
6. wines_tried
7. avg_ratings_per_wine
8. coefficient_of_variation

### 2. Wine Type Preferences (6)
9. red_wine_preference
10. white_wine_preference
11. sparkling_wine_preference
12. rose_wine_preference
13. dessert_wine_preference
14. dessert_port_wine_preference

### 3. ABV Preferences (3)
15. weighted_abv_preference
16. avg_abv_tried
17. high_vs_low_abv_preference

### 4. Body Type Preferences (5)
18. very_light_bodied_preference
19. light_bodied_preference
20. medium_bodied_preference
21. full_bodied_preference
22. very_full_bodied_preference

### 5. Acidity Preferences (3)
23. low_acidity_preference
24. medium_acidity_preference
25. high_acidity_preference

### 6. Country Preferences (5)
26. country_1_preference
27. country_2_preference
28. country_3_preference
29. country_4_preference
30. country_5_preference

### 7. Grape Preferences (5)
31. grape_1_preference
32. grape_2_preference
33. grape_3_preference
34. grape_4_preference
35. grape_5_preference

### 8. Complexity Preferences (2)
36. complexity_preference
37. avg_complexity_tried

### 9. Quality Indicators (2)
38. reserve_preference
39. grand_preference

### 10. Rating Patterns (8)
40. high_rating_proportion
41. low_rating_proportion
42. rating_entropy
43. rating_1_proportion
44. rating_2_proportion
45. rating_3_proportion
46. rating_4_proportion
47. rating_5_proportion

### 11. Diversity Metrics (4)
48. rating_range
49. rating_variance
50. unique_ratings_count
51. rating_skewness

### 12. Temporal Patterns (4)
52. date_range_days
55. avg_days_between_ratings
54. rating_trend
55. rating_frequency

## Response Format

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

## Python Example

```python
import requests
import json

# Comprehensive user features
user_features = {
    "rating_mean": 3.8,
    "rating_std": 0.95,
    "rating_count": 150,
    # ... all 55 features ...
    "rating_frequency": 0.41
}

response = requests.post(
    "http://localhost:8080/wines",
    json=user_features
)

recommendations = response.json()
print(f"Recommended wines: {recommendations['wines']}")
print(f"Similarity scores: {recommendations['scores']}")
```

## Notes

- All 55 features are **required** when using comprehensive format
- Features are automatically ordered correctly by `USER_FEATURE_NAMES`
- The API auto-detects format based on presence of `rating_mean` field
- Legacy simple format (type, body, dryness, abv) is still supported for backward compatibility
