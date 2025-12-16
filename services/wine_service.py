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
        Convert dot product distances to similarity scores.

        The index uses DOT_PRODUCT_DISTANCE and returns raw dot product values.
        For normalized embeddings, dot product ranges from -1 to 1, where:
        - 1.0 = identical vectors (most similar)
        - 0.0 = orthogonal vectors (unrelated)
        - -1.0 = opposite vectors (most dissimilar)

        We transform to [0, 1] range using: score = (1 + dot_product) / 2

        Args:
            wine_ids: List of wine IDs
            distances: List of dot product values from the vector index

        Returns:
            Dictionary mapping wine IDs to similarity scores in [0, 1] range
        """
        if not distances:
            return {}
            
        scores = {}

        # Transform dot product [-1, 1] to similarity score [0, 1]
        # score = (1 + dot_product) / 2
        for wine_id, dot_product in zip(wine_ids, distances):
            scores[wine_id] = (1.0 + dot_product) / 2.0

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
        #user_embedding = self.model_service.generate_user_embedding(user_preferences)
        user_embedding = [
                            -0.05860693,
                            -0.020373588,
                            0.09871534,
                            -0.005983068,
                            0.09388827,
                            -0.066756405,
                            0.1408568,
                            -0.049743503,
                            0.13870236,
                            -0.14746328,
                            0.019605873,
                            0.01515809,
                            -0.067578785,
                            0.032145724,
                            -0.010749513,
                            -0.082488365,
                            0.0357483,
                            0.06814065,
                            0.029584263,
                            -0.1011323,
                            0.034799986,
                            -0.29360127,
                            0.09167781,
                            -0.17788845,
                            -0.05486826,
                            -0.0015850719,
                            -0.12520334,
                            0.06378981,
                            0.08631343,
                            -0.08516686,
                            0.078578785,
                            0.019061964,
                            -0.1374311,
                            0.14390196,
                            -0.14011416,
                            -0.021555018,
                            0.030216366,
                            -0.013124545,
                            -0.08414835,
                            -0.1086595,
                            0.036855552,
                            0.12947054,
                            -0.05272462,
                            0.0783867,
                            0.058192387,
                            0.0021834688,
                            0.10368838,
                            0.23364341,
                            0.017185815,
                            0.0019084179,
                            0.12527849,
                            0.06148894,
                            0.08165215,
                            -0.008029294,
                            -0.14374016,
                            0.08788495,
                            -0.03322588,
                            -0.09847723,
                            -0.089679055,
                            0.111746795,
                            0.010611362,
                            0.056944612,
                            -0.061945822,
                            0.07284319,
                            0.006215827,
                            0.060238056,
                            -0.07764083,
                            -0.08978784,
                            -0.09791995,
                            -0.0006756511,
                            0.03560769,
                            -0.02327511,
                            -0.16467074,
                            0.0031122558,
                            0.0007117311,
                            -0.02547811,
                            0.06838836,
                            -0.022168413,
                            0.07126349,
                            -0.060974922,
                            -0.15344442,
                            -0.07870428,
                            -0.02275321,
                            0.046778493,
                            0.14494751,
                            0.14430894,
                            -0.04496597,
                            -0.124737695,
                            0.048849486,
                            -0.08222944,
                            0.20506242,
                            0.04726016,
                            0.06358253,
                            0.038415004,
                            0.05316861,
                            0.3309316,
                            0.0119034,
                            -0.109198354,
                            -0.098689966,
                            0.1083388,
                            0.017464496,
                            -0.020610882,
                            -0.13216555,
                            0.14152297,
                            -0.024256302,
                            -0.029898189,
                            -0.008023574,
                            -0.0946877,
                            0.011439868,
                            0.0065996386,
                            0.05938025,
                            -0.027862506,
                            -0.025274625,
                            0.082682185,
                            -0.04034877,
                            -0.06400985,
                            0.0025860814
                        ]
        
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
