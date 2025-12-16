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

from schemas import WINE_SCHEMA, WINE_QUERY_SCHEMA
from config import INDEX_ENDPOINT, DEPLOYED_INDEX_ID
from utils.logging import logger

if TYPE_CHECKING:
    from services.model_service import ModelService
    from services.embeddings_service import EmbeddingsService


class WineService:
    """Service for wine vector search and recommendation using pre-calculated wine embeddings."""

    def __init__(
        self,
        vector_search_client: aiplatform_v1.MatchServiceClient,
        model_service: Optional['ModelService'] = None,
        embeddings_service: Optional['EmbeddingsService'] = None,
        similarity_service: Optional[Any] = None  # Deprecated: not used with dot product model
    ):
        """
        Initialize the wine service.

        Args:
            vector_search_client: Initialized Vertex AI Match Service client
            model_service: Optional ModelService for generating user embeddings
            embeddings_service: Optional EmbeddingsService for scoring specific wines
            similarity_service: Deprecated parameter (kept for backward compatibility, ignored)
        """
        self.vector_search_client = vector_search_client
        self.model_service = model_service
        self.embeddings_service = embeddings_service
        # similarity_service is deprecated - dot product model doesn't need it
        logger.info(
            "WineService initialized",
            extra={
                "has_model_service": model_service is not None,
                "has_embeddings_service": embeddings_service is not None,
                "model_type": "dot_product",
                "output_format": "raw_dot_products"
            }
        )
    
    def normalize_distances(self, wine_ids: List[str], distances: List[float]) -> Dict[str, float]:
        """
        Map wine IDs to their dot product distances.

        The index uses DOT_PRODUCT_DISTANCE and returns raw dot product values.
        For normalized embeddings, dot product ranges from -1 to 1, where:
        - 1.0 = identical vectors (most similar)
        - 0.0 = orthogonal vectors (unrelated)
        - -1.0 = opposite vectors (most dissimilar)

        The backend is responsible for transforming these to final ratings.

        Args:
            wine_ids: List of wine IDs
            distances: List of dot product values from the vector index

        Returns:
            Dictionary mapping wine IDs to dot product values
        """
        if not distances:
            return {}

        dot_products = {}

        min_dot = min(distances)
        max_dot = max(distances)
        mean_dot = sum(distances) / len(distances)
        dot_range = max_dot - min_dot

        logger.info(
            "Mapping wine IDs to dot products",
            extra={
                "count": len(distances),
                "min_dot_product": min_dot,
                "max_dot_product": max_dot,
                "mean_dot_product": mean_dot,
                "dot_product_range": dot_range,
                "raw_dot_products": distances[:10] if len(distances) >= 10 else distances
            }
        )

        for wine_id, dot_product in zip(wine_ids, distances):
            dot_products[wine_id] = dot_product

        logger.info(
            "Dot product mapping complete",
            extra={
                "wines_mapped": len(dot_products),
                "top_5_dot_products": sorted(dot_products.values(), reverse=True)[:5],
                "bottom_5_dot_products": sorted(dot_products.values())[:5] if len(dot_products) >= 5 else list(dot_products.values())
            }
        )

        return dot_products
    
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
            Tuple of (wine_ids, dot_products) where dot_products is a dict mapping IDs to raw dot product values

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
        wine_ids, dot_products = self.find_similar_wines(user_embedding, neighbor_count)

        logger.info("Wine recommendations retrieved", extra={"count": len(wine_ids)})
        return wine_ids, dot_products
    
    def find_similar_wines(
        self,
        wine_vector: List[float],
        neighbor_count: int = 10,
        use_similarity_layer: bool = False  # Deprecated: dot product model doesn't need similarity layer
    ) -> Tuple[List[str], Dict[str, float]]:
        """
        Find similar wines using vector search and return raw dot products.

        Uses the vector index to find nearest neighbors based on dot product similarity.
        Returns raw dot product values without transformation.

        Args:
            wine_vector: User embedding vector (normalized, 117 dimensions)
            neighbor_count: Number of similar wines to return
            use_similarity_layer: Deprecated parameter (kept for backward compatibility, ignored)

        Returns:
            Tuple of (wine_ids, dot_products) where dot_products is a dict mapping IDs to raw dot product values

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
        
        try:
            response = self.vector_search_client.find_neighbors(request_obj)
        except Exception as e:
            logger.error(
                "Vector search failed",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "index_endpoint": INDEX_ENDPOINT,
                    "deployed_index_id": DEPLOYED_INDEX_ID
                }
            )
            raise

        # Log response structure for debugging
        logger.info(
            "Vector search response received",
            extra={
                "has_nearest_neighbors": hasattr(response, 'nearest_neighbors'),
                "nearest_neighbors_count": len(response.nearest_neighbors) if hasattr(response, 'nearest_neighbors') else 0,
                "response_type": type(response).__name__
            }
        )

        if not response.nearest_neighbors or len(response.nearest_neighbors) == 0:
            logger.warning("Vector search returned no neighbors")
            return [], {}

        # Check if the first query result has neighbors
        first_result = response.nearest_neighbors[0]
        neighbor_count = len(first_result.neighbors) if hasattr(first_result, 'neighbors') else 0

        logger.info(
            "Vector search first result",
            extra={
                "neighbor_count": neighbor_count,
                "has_neighbors_attr": hasattr(first_result, 'neighbors')
            }
        )

        if not first_result.neighbors or neighbor_count == 0:
            logger.warning("Vector search returned empty neighbor list")
            return [], {}

        wine_neighbors = []
        distances = []

        try:
            for neighbor in response.nearest_neighbors[0].neighbors:
                datapoint_id = neighbor.datapoint.datapoint_id
                wine_neighbors.append(datapoint_id)
                distances.append(neighbor.distance)  # This is the dot product
        except Exception as e:
            logger.error(
                "Error processing vector search results",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise
        
        logger.info(
            "Vector search completed",
            extra={
                "wine_count": len(wine_neighbors),
                "raw_dot_products_sample": distances[:5] if len(distances) >= 5 else distances
            }
        )

        # Map wine IDs to raw dot products (backend handles score transformation)
        dot_products = self.normalize_distances(wine_neighbors, distances)
        return wine_neighbors, dot_products

    def score_wines(
        self,
        user_embedding: List[float],
        wine_ids: List[str]
    ) -> Dict[str, float]:
        """
        Calculate dot products for specific wines using O(1) lookup.

        This method retrieves wine embeddings from the embeddings service and
        calculates dot products between user and wine embeddings. The backend
        is responsible for transforming these to final scores/ratings.

        Args:
            user_embedding: User embedding vector (117 dimensions)
            wine_ids: List of wine IDs to score

        Returns:
            Dictionary mapping wine IDs to dot product values (typically in [-1, 1] range for normalized vectors)

        Raises:
            ValueError: If embeddings service is not initialized
        """
        if not self.embeddings_service:
            raise ValueError("Embeddings service not initialized")

        import numpy as np

        logger.info(
            "Calculating dot products for specific wines",
            extra={
                "wine_count": len(wine_ids),
                "user_embedding_dim": len(user_embedding)
            }
        )

        # Load wine embeddings (O(1) per wine)
        wine_embeddings = self.embeddings_service.get_embeddings(wine_ids)

        if not wine_embeddings:
            logger.warning("No wine embeddings found for provided IDs")
            return {}

        # Calculate dot products
        dot_products = {}
        user_vec = np.array(user_embedding)

        for wine_id, wine_embedding in wine_embeddings.items():
            wine_vec = np.array(wine_embedding)
            # Calculate dot product
            dot_product = float(np.dot(user_vec, wine_vec))
            dot_products[wine_id] = dot_product

        logger.info(
            "Dot product calculation complete",
            extra={
                "wines_requested": len(wine_ids),
                "wines_calculated": len(dot_products),
                "wines_not_found": len(wine_ids) - len(dot_products),
                "dot_products_range": [min(dot_products.values()), max(dot_products.values())] if dot_products else [0, 0],
                "mean_dot_product": sum(dot_products.values()) / len(dot_products) if dot_products else 0
            }
        )

        return dot_products
