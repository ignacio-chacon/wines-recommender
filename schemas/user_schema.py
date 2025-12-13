# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Feature names in order for the 55-dimensional user feature vector
USER_FEATURE_NAMES = [
    # Basic features (8)
    "rating_mean",
    "rating_std",
    "rating_count",
    "rating_min",
    "rating_max",
    "wines_tried",
    "avg_ratings_per_wine",
    "coefficient_of_variation",
    
    # Wine type preferences (6)
    "red_wine_preference",
    "white_wine_preference",
    "sparkling_wine_preference",
    "rose_wine_preference",
    "dessert_wine_preference",
    "dessert_port_wine_preference",
    
    # ABV preferences (3)
    "weighted_abv_preference",
    "avg_abv_tried",
    "high_vs_low_abv_preference",
    
    # Body type preferences (5)
    "very_light_bodied_preference",
    "light_bodied_preference",
    "medium_bodied_preference",
    "full_bodied_preference",
    "very_full_bodied_preference",
    
    # Acidity preferences (3)
    "low_acidity_preference",
    "medium_acidity_preference",
    "high_acidity_preference",
    
    # Country preferences (5)
    "country_1_preference",
    "country_2_preference",
    "country_3_preference",
    "country_4_preference",
    "country_5_preference",
    
    # Grape preferences (5)
    "grape_1_preference",
    "grape_2_preference",
    "grape_3_preference",
    "grape_4_preference",
    "grape_5_preference",
    
    # Complexity preferences (2)
    "complexity_preference",
    "avg_complexity_tried",
    
    # Quality indicators (2)
    "reserve_preference",
    "grand_preference",
    
    # Rating patterns (8)
    "high_rating_proportion",
    "low_rating_proportion",
    "rating_entropy",
    "rating_1_proportion",
    "rating_2_proportion",
    "rating_3_proportion",
    "rating_4_proportion",
    "rating_5_proportion",
    
    # Diversity metrics (4)
    "rating_range",
    "rating_variance",
    "unique_ratings_count",
    "rating_skewness",
    
    # Temporal patterns (4)
    "date_range_days",
    "avg_days_between_ratings",
    "rating_trend",
    "rating_frequency"
]

# Flattened User Features Schema - accepts key:value pairs for all 55 features
USER_FEATURES_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        # Basic features (8)
        "rating_mean": {"type": "number", "description": "Average rating given by user"},
        "rating_std": {"type": "number", "minimum": 0, "description": "Standard deviation of ratings"},
        "rating_count": {"type": "number", "minimum": 0, "description": "Total number of ratings"},
        "rating_min": {"type": "number", "minimum": 0, "maximum": 5, "description": "Minimum rating given"},
        "rating_max": {"type": "number", "minimum": 0, "maximum": 5, "description": "Maximum rating given"},
        "wines_tried": {"type": "number", "minimum": 0, "description": "Number of unique wines rated"},
        "avg_ratings_per_wine": {"type": "number", "minimum": 0, "description": "Average ratings per wine"},
        "coefficient_of_variation": {"type": "number", "description": "Rating std / mean"},
        
        # Wine type preferences (6)
        "red_wine_preference": {"type": "number", "description": "Weighted average rating for red wines"},
        "white_wine_preference": {"type": "number", "description": "Weighted average rating for white wines"},
        "sparkling_wine_preference": {"type": "number", "description": "Weighted average rating for sparkling wines"},
        "rose_wine_preference": {"type": "number", "description": "Weighted average rating for rosé wines"},
        "dessert_wine_preference": {"type": "number", "description": "Weighted average rating for dessert wines"},
        "dessert_port_wine_preference": {"type": "number", "description": "Weighted average rating for dessert/port wines"},
        
        # ABV preferences (3)
        "weighted_abv_preference": {"type": "number", "description": "ABV weighted by ratings"},
        "avg_abv_tried": {"type": "number", "description": "Average ABV of wines tried"},
        "high_vs_low_abv_preference": {"type": "number", "description": "High ABV rating - Low ABV rating"},
        
        # Body type preferences (5)
        "very_light_bodied_preference": {"type": "number", "description": "Weighted rating for very light-bodied wines"},
        "light_bodied_preference": {"type": "number", "description": "Weighted rating for light-bodied wines"},
        "medium_bodied_preference": {"type": "number", "description": "Weighted rating for medium-bodied wines"},
        "full_bodied_preference": {"type": "number", "description": "Weighted rating for full-bodied wines"},
        "very_full_bodied_preference": {"type": "number", "description": "Weighted rating for very full-bodied wines"},
        
        # Acidity preferences (3)
        "low_acidity_preference": {"type": "number", "description": "Weighted rating for low acidity wines"},
        "medium_acidity_preference": {"type": "number", "description": "Weighted rating for medium acidity wines"},
        "high_acidity_preference": {"type": "number", "description": "Weighted rating for high acidity wines"},
        
        # Country preferences (5)
        "country_1_preference": {"type": "number", "description": "Top country #1 preference"},
        "country_2_preference": {"type": "number", "description": "Top country #2 preference"},
        "country_3_preference": {"type": "number", "description": "Top country #3 preference"},
        "country_4_preference": {"type": "number", "description": "Top country #4 preference"},
        "country_5_preference": {"type": "number", "description": "Top country #5 preference"},
        
        # Grape preferences (5)
        "grape_1_preference": {"type": "number", "description": "Top grape #1 preference"},
        "grape_2_preference": {"type": "number", "description": "Top grape #2 preference"},
        "grape_3_preference": {"type": "number", "description": "Top grape #3 preference"},
        "grape_4_preference": {"type": "number", "description": "Top grape #4 preference"},
        "grape_5_preference": {"type": "number", "description": "Top grape #5 preference"},
        
        # Complexity preferences (2)
        "complexity_preference": {"type": "number", "description": "Complex wine rating - Simple wine rating"},
        "avg_complexity_tried": {"type": "number", "description": "Average complexity level of wines tried"},
        
        # Quality indicators (2)
        "reserve_preference": {"type": "number", "description": "Reserve wine rating - Non-reserve wine rating"},
        "grand_preference": {"type": "number", "description": "Grand wine rating - Non-grand wine rating"},
        
        # Rating patterns (8)
        "high_rating_proportion": {"type": "number", "minimum": 0, "maximum": 1, "description": "Proportion of 4-5 star ratings"},
        "low_rating_proportion": {"type": "number", "minimum": 0, "maximum": 1, "description": "Proportion of 1-2 star ratings"},
        "rating_entropy": {"type": "number", "minimum": 0, "description": "Entropy of rating distribution"},
        "rating_1_proportion": {"type": "number", "minimum": 0, "maximum": 1, "description": "Proportion of 1-star ratings"},
        "rating_2_proportion": {"type": "number", "minimum": 0, "maximum": 1, "description": "Proportion of 2-star ratings"},
        "rating_3_proportion": {"type": "number", "minimum": 0, "maximum": 1, "description": "Proportion of 3-star ratings"},
        "rating_4_proportion": {"type": "number", "minimum": 0, "maximum": 1, "description": "Proportion of 4-star ratings"},
        "rating_5_proportion": {"type": "number", "minimum": 0, "maximum": 1, "description": "Proportion of 5-star ratings"},
        
        # Diversity metrics (4)
        "rating_range": {"type": "number", "minimum": 0, "description": "Difference between max and min ratings"},
        "rating_variance": {"type": "number", "minimum": 0, "description": "Variance of user's ratings"},
        "unique_ratings_count": {"type": "number", "minimum": 0, "description": "Number of different rating values used"},
        "rating_skewness": {"type": "number", "description": "Skewness of rating distribution"},
        
        # Temporal patterns (4)
        "date_range_days": {"type": "number", "minimum": 0, "description": "Days between first and last rating"},
        "avg_days_between_ratings": {"type": "number", "minimum": 0, "description": "Average days between consecutive ratings"},
        "rating_trend": {"type": "number", "description": "Linear trend in ratings over time"},
        "rating_frequency": {"type": "number", "minimum": 0, "description": "Ratings per day"}
    },
    "required": USER_FEATURE_NAMES,
    "additionalProperties": False
}

# Legacy simple preference schema for backward compatibility
SIMPLE_USER_PREFERENCES_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["Red", "White", "Rose", "Sparkling"]},
        "body": {"type": "integer", "minimum": 1, "maximum": 5},
        "dryness": {"type": "integer", "minimum": 1, "maximum": 5},
        "abv": {"type": "number", "minimum": 0, "maximum": 25}
    },
    "required": ["type", "body", "dryness", "abv"]
}

# Aliases
USER_PREFERENCES_SCHEMA = USER_FEATURES_SCHEMA  # Primary schema
WINE_QUERY_SCHEMA = SIMPLE_USER_PREFERENCES_SCHEMA  # Legacy compatibility