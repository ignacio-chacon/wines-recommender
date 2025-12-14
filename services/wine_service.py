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

from typing import Dict, List, Tuple, Optional, TYPE_CHECKING
import jsonschema
from google.cloud import aiplatform_v1

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
        model_service: Optional['ModelService'] = None
    ):
        """
        Initialize the wine service.
        
        Args:
            vector_search_client: Initialized Vertex AI Match Service client
            model_service: Optional ModelService for generating user embeddings
        """
        self.vector_search_client = vector_search_client
        self.model_service = model_service
        logger.info("WineService initialized", extra={"has_model_service": model_service is not None})
    
    def normalize_distances(self, wine_ids: List[str], distances: List[float]) -> Dict[str, float]:
        """
        Normalize distances to 0-1 scores using min-max normalization.
        
        Args:
            wine_ids: List of wine IDs
            distances: List of corresponding distances
            
        Returns:
            Dictionary mapping wine IDs to normalized scores
        """
        if not distances:
            return {}
        
        min_dist = min(distances)
        max_dist = max(distances)
        scores = {}
        
        if max_dist > min_dist:
            for wine_id, dist in zip(wine_ids, distances):
                scores[wine_id] = (dist - min_dist) / (max_dist - min_dist)
        else:
            # All distances are the same
            for wine_id in wine_ids:
                scores[wine_id] = 1.0
        
        return scores
    
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
    
    def find_similar_wines(self, wine_vector: List[float], neighbor_count: int = 10) -> Tuple[List[str], Dict[str, float]]:
        """
        Find similar wines using vector search.
        
        Args:
            wine_vector: Feature vector representing wine properties
            neighbor_count: Number of similar wines to return
            
        Returns:
            Tuple of (wine_ids, scores) where scores is a dict mapping IDs to similarity scores
            
        Raises:
            Exception: If the vector search fails
        """
        # Build FindNeighborsRequest object
        datapoint = aiplatform_v1.IndexDatapoint(feature_vector=wine_vector)
        query = aiplatform_v1.FindNeighborsRequest.Query(
            datapoint=datapoint, 
            neighbor_count=neighbor_count
        )
        request_obj = aiplatform_v1.FindNeighborsRequest(
            index_endpoint=INDEX_ENDPOINT,
            deployed_index_id=DEPLOYED_INDEX_ID,
            queries=[query],
            return_full_datapoint=False,
        )
        
        response = self.vector_search_client.find_neighbors(request_obj)
        wine_neighbors = []
        distances = []
        
        # Collect all neighbors and distances
        for neighbor in response.nearest_neighbors[0].neighbors:
            datapoint_id = neighbor.datapoint.datapoint_id
            wine_neighbors.append(datapoint_id)
            distances.append(neighbor.distance)
        
        # Normalize distances to scores
        scores = self.normalize_distances(wine_neighbors, distances)
        
        return wine_neighbors, scores
