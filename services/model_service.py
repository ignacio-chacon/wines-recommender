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

from typing import Dict, List, Any
import jsonschema
from google.cloud import aiplatform

from schemas import (
    USER_FEATURE_NAMES,
    USER_FEATURES_SCHEMA,
    SIMPLE_USER_PREFERENCES_SCHEMA
)
from utils.logging import logger
import config


class ModelService:
    """Service for generating user embeddings using the Two Tower Model with 55 comprehensive features."""
    
    def __init__(self, endpoint_name: str = None):
        """
        Initialize the model service.
        
        Args:
            endpoint_name: Full endpoint resource name. If None, will be constructed from config.
        """
        if endpoint_name:
            self.endpoint_name = endpoint_name
        elif config.MODEL_ENDPOINT:
            self.endpoint_name = config.MODEL_ENDPOINT
        else:
            # Construct from individual components
            self.endpoint_name = (
                f"projects/{config.MODEL_PROJECT_ID}/"
                f"locations/{config.MODEL_LOCATION}/"
                f"endpoints/{config.MODEL_ENDPOINT_ID}"
            )
        
        # Initialize the Vertex AI client
        aiplatform.init(
            project=config.MODEL_PROJECT_ID,
            location=config.MODEL_LOCATION
        )
        
        logger.info("ModelService initialized", extra={"endpoint": self.endpoint_name})
    
    def validate_user_features(self, data: Dict) -> None:
        """
        Validate flattened user features against schema.
        
        Args:
            data: Dictionary containing user features as key:value pairs (55 features)
            
        Raises:
            ValueError: If validation fails
        """
        try:
            jsonschema.validate(instance=data, schema=USER_FEATURES_SCHEMA)
        except jsonschema.ValidationError as ve:
            raise ValueError(f"User features validation error: {ve.message}")
    
    def validate_simple_preferences(self, data: Dict) -> None:
        """
        Validate simple user preferences (legacy format).
        
        Args:
            data: Dictionary containing simple preferences (type, body, dryness, abv)
            
        Raises:
            ValueError: If validation fails
        """
        try:
            jsonschema.validate(instance=data, schema=SIMPLE_USER_PREFERENCES_SCHEMA)
        except jsonschema.ValidationError as ve:
            raise ValueError(f"Simple preferences validation error: {ve.message}")
    
    def features_dict_to_vector(self, features_dict: Dict) -> List[float]:
        """
        Convert flattened feature dictionary to ordered 55-dimensional vector.
        
        Args:
            features_dict: Dictionary with feature names as keys
            
        Returns:
            List of 55 floats in the correct order defined by USER_FEATURE_NAMES
        """
        return [float(features_dict[name]) for name in USER_FEATURE_NAMES]
    
    def preprocess_user_data(self, data: Dict) -> List[float]:
        """
        Preprocess user data for model input.
        
        Supports both comprehensive feature format (55 features) and simple legacy format.
        
        Args:
            data: Dictionary containing either:
                  - Flattened user features (key:value pairs, 55 features)
                  - Simple preferences (type, body, dryness, abv)
            
        Returns:
            List of 55 floats ready for model prediction
            
        Raises:
            ValueError: If the data doesn't contain comprehensive features
        """
        if 'rating_mean' in data:
            self.validate_user_features(data)
            
            # Convert to ordered vector of 55 floats
            feature_vector = self.features_dict_to_vector(data)
            
            logger.info(
                "Comprehensive user features preprocessed",
                extra={"feature_count": len(feature_vector)}
            )
            
            return feature_vector
            
        else:
            raise ValueError(
                "Two Tower Model requires comprehensive user features (55 features). "
                "Simple preferences format is not supported. "
                "Please provide all required user features."
            )
    
    def generate_user_embedding(self, user_data: Dict) -> List[float]:
        """
        Generate user embedding using the Two Tower Model.
        
        Args:
            user_data: Dictionary containing flattened user features (55 key:value pairs)
            
        Returns:
            List of floats representing the user embedding vector
            
        Raises:
            ValueError: If input validation fails
            Exception: If model prediction fails
        """
        logger.info(
            "Generating user embedding",
            extra={
                "format": "comprehensive_features",
                "feature_count": 55
            }
        )

        # Preprocess the input data - returns list of 55 floats
        feature_vector = self.preprocess_user_data(user_data)
        
        try:
            # Get the endpoint
            endpoint = aiplatform.Endpoint(self.endpoint_name)
            
            # Make prediction with the feature vector
            # The endpoint expects: {"instances": [[...55 floats...]]}
            logger.info("Calling model endpoint for prediction")
            prediction = endpoint.predict(instances=[feature_vector])
            
            # Extract embedding from prediction
            # The response format should be: {"predictions": [[...embedding...]]}
            if hasattr(prediction, 'predictions') and len(prediction.predictions) > 0:
                embedding = prediction.predictions[0]
                
                # Ensure it's a list of floats
                if isinstance(embedding, list):
                    user_embedding = [float(x) for x in embedding]
                elif hasattr(embedding, 'tolist'):
                    # Handle numpy arrays
                    user_embedding = [float(x) for x in embedding.tolist()]
                else:
                    raise Exception(f"Unexpected embedding format: {type(embedding)}")
                
                logger.info(
                    "User embedding generated successfully", 
                    extra={
                        "embedding_dim": len(user_embedding),
                        "input_features": len(feature_vector)
                    }
                )
                return user_embedding
            else:
                raise Exception("No predictions returned from model endpoint")
                
        except Exception as e:
            logger.error(
                "Failed to generate user embedding", 
                extra={"error": str(e), "endpoint": self.endpoint_name}
            )
            raise Exception(f"Model prediction failed: {str(e)}")
