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

from typing import Dict, List, Tuple, Optional, TYPE_CHECKING, Any
import jsonschema
from google.cloud import aiplatform_v1
from scipy.special import expit

from schemas import WINE_SCHEMA, WINE_QUERY_SCHEMA
from config import INDEX_ENDPOINT, DEPLOYED_INDEX_ID
from utils.logging import logger

if TYPE_CHECKING:
    from services.model_service import ModelService


class WineService:
    """Service for wine vector search and recommendation using pre-calculated wine embeddings."""
    
    def __init__(
        self, 
        vector_search_client: aiplatform_v1.MatchServiceClient,
        model_service: Optional['ModelService'] = None,
    ):
        """
        Initialize the wine service.
        
        Args:
            vector_search_client: Initialized Vertex AI Match Service client
            model_service: Optional ModelService for generating user embeddings
            similarity_service: Deprecated parameter (kept for backward compatibility, ignored)
        """
        self.vector_search_client = vector_search_client
        self.model_service = model_service
        logger.info(
            "WineService initialized",
            extra={
                "has_model_service": model_service is not None,
                "model_type": "dot_product",
                "rating_method": "sigmoid(dot_product) * 4 + 1"
            }
        )
    
    def normalize_distances(self, wine_ids: List[str], distances: List[float]) -> Dict[str, float]:
        """
        Convert dot product distances to ratings in [1, 5] range.

        The index uses DOT_PRODUCT_DISTANCE and returns raw dot product values.
        For normalized embeddings, dot product ranges from -1 to 1, where:
        - 1.0 = identical vectors (most similar)
        - 0.0 = orthogonal vectors (unrelated)
        - -1.0 = opposite vectors (most dissimilar)

        We transform to [1, 5] rating range using: rating = sigmoid(dot_product) * 4 + 1
        This matches the dot product model's training transformation.

        Args:
            wine_ids: List of wine IDs
            distances: List of dot product values from the vector index

        Returns:
            Dictionary mapping wine IDs to predicted ratings in [1, 5] range
        """
        if not distances:
            return {}
            
        ratings = {}
        
        min_dot = min(distances)
        max_dot = max(distances)
        mean_dot = sum(distances) / len(distances)
        dot_range = max_dot - min_dot
        
        logger.info(
            "Transforming dot products to ratings",
            extra={
                "count": len(distances),
                "min_dot_product": min_dot,
                "max_dot_product": max_dot,
                "mean_dot_product": mean_dot,
                "dot_product_range": dot_range,
                "raw_dot_products": distances[:10] if len(distances) >= 10 else distances,
                "transformation": "sigmoid(dot_product) * 4 + 1"
            }
        )

        for wine_id, dot_product in zip(wine_ids, distances):
            # Use sigmoid transformation to match model training
            # sigmoid(dot_product) maps [-1, 1] to [0, 1]
            # * 4 scales to [0, 4]
            # + 1 shifts to [1, 5]
            ratings[wine_id] = expit(dot_product) * 4 + 1
        
        min_rating = min(ratings.values())
        max_rating = max(ratings.values())
        mean_rating = sum(ratings.values()) / len(ratings)
        
        logger.info(
            "Rating calculation complete",
            extra={
                "min_rating": min_rating,
                "max_rating": max_rating,
                "mean_rating": mean_rating,
                "rating_range": max_rating - min_rating,
                "top_5_ratings": sorted(ratings.values(), reverse=True)[:5],
                "bottom_5_ratings": sorted(ratings.values())[:5] if len(ratings) >= 5 else list(ratings.values())
            }
        )

        return ratings
    
    # Deprecated: compute_ratings_with_similarity_layer method removed
    # The dot product model uses sigmoid(dot_product) * 4 + 1 directly
    # No similarity layer service needed
    
    def get_wine_recommendations(
        self, 
        user_preferences: Dict, 
        user_id: Optional[str] = None,
        neighbor_count: int = 10
    ) -> Tuple[List[str], Dict[str, float]]:
        """
        Get wine recommendations using the Two Tower Model.
        
        This method uses the model service to generate a user embedding from preferences,
        then searches for similar wines using the pre-calculated wine embeddings in the vector index.
        
        Args:
            user_preferences: Dictionary containing user wine preferences
            user_id: Optional user ID (GUID) for tracking (not currently used, reserved for future use)
            neighbor_count: Number of wine recommendations to return
            
        Returns:
            Tuple of (wine_ids, scores) where scores is a dict mapping IDs to similarity scores
            
        Raises:
            ValueError: If model service is not initialized
            Exception: If embedding generation or vector search fails
        """
        
        logger.info(
            "Getting wine recommendations", 
            extra={"preferences": user_preferences, "user_id": user_id}
        )
        
        # Generate user embedding using the Two Tower Model
        user_embedding = self.model_service.generate_user_embedding(user_preferences)
        
        logger.info(
            "User embedding generated, searching for similar wines",
            extra={"embedding_dim": len(user_embedding)}
        )
        
        # Find similar wines using the user embedding
        wine_ids, scores = self.find_similar_wines(user_embedding, neighbor_count)
        
        logger.info("Wine recommendations retrieved", extra={"count": len(wine_ids)})
        return wine_ids, scores
    
    def find_similar_wines(
        self,
        wine_vector: List[float],
        neighbor_count: int = 10,
        use_similarity_layer: bool = False  # Deprecated: dot product model doesn't need similarity layer
    ) -> Tuple[List[str], Dict[str, float]]:
        """
        Find similar wines using vector search and compute ratings.
        
        Uses dot product directly with sigmoid transformation to compute ratings in [1, 5] range.
        This matches the dot product model's training transformation.
        
        Args:
            wine_vector: User embedding vector (normalized, 117 dimensions)
            neighbor_count: Number of similar wines to return
            use_similarity_layer: Deprecated parameter (kept for backward compatibility, ignored)
            
        Returns:
            Tuple of (wine_ids, ratings) where ratings is a dict mapping IDs to ratings in [1, 5] range
            
        Raises:
            Exception: If the vector search fails
        """
        import numpy as np
        
        query_norm = np.linalg.norm(wine_vector)
        query_min = min(wine_vector)
        query_max = max(wine_vector)
        query_mean = sum(wine_vector) / len(wine_vector)
        
        logger.info(
            "Querying vector index for similar wines",
            extra={
                "query_vector_norm": query_norm,
                "query_vector_dim": len(wine_vector),
                "query_vector_min": query_min,
                "query_vector_max": query_max,
                "query_vector_mean": query_mean,
                "is_normalized": abs(query_norm - 1.0) < 0.01,
                "neighbor_count": neighbor_count,
                "model_type": "dot_product"
            }
        )
        
        # No need to fetch full datapoints - we only need dot products
        datapoint = aiplatform_v1.IndexDatapoint(feature_vector=wine_vector)
        query = aiplatform_v1.FindNeighborsRequest.Query(
            datapoint=datapoint, 
            neighbor_count=neighbor_count
        )
        request_obj = aiplatform_v1.FindNeighborsRequest(
            index_endpoint=INDEX_ENDPOINT,
            deployed_index_id=DEPLOYED_INDEX_ID,
            queries=[query],
            return_full_datapoint=False,  # Not needed for dot product model
        )
        
        response = self.vector_search_client.find_neighbors(request_obj)
        wine_neighbors = []
        distances = []
        
        for neighbor in response.nearest_neighbors[0].neighbors:
            datapoint_id = neighbor.datapoint.datapoint_id
            wine_neighbors.append(datapoint_id)
            distances.append(neighbor.distance)  # This is the dot product
        
        logger.info(
            "Vector search completed",
            extra={
                "wine_count": len(wine_neighbors),
                "raw_dot_products_sample": distances[:5] if len(distances) >= 5 else distances
            }
        )
        
        # Convert dot products to ratings using sigmoid transformation
        # This matches the model's training: sigmoid(dot_product) * 4 + 1
        ratings = self.normalize_distances(wine_neighbors, distances)
        return wine_neighbors, ratings
