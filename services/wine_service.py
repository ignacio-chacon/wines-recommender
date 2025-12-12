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

from typing import Dict, List, Tuple
import jsonschema
from google.cloud import aiplatform_v1

from schemas import WINE_SCHEMA
from config import INDEX_ENDPOINT, DEPLOYED_INDEX_ID


class WineService:
    """Service for wine vector search and recommendation."""
    
    def __init__(self, vector_search_client: aiplatform_v1.MatchServiceClient):
        """
        Initialize the wine service.
        
        Args:
            vector_search_client: Initialized Vertex AI Match Service client
        """
        self.vector_search_client = vector_search_client
    
    def parse_wine_vector(self, data: Dict) -> List[float]:
        """
        Parse and validate wine data, converting it to a feature vector.
        
        Args:
            data: Dictionary containing wine properties
            
        Returns:
            List of floats representing the wine feature vector
            
        Raises:
            ValueError: If validation fails or data is invalid
        """
        try:
            jsonschema.validate(instance=data, schema=WINE_SCHEMA)
            wine_type = data["type"].lower()
            is_rose = 1 if wine_type == "rose" else 0
            is_sparkling = 1 if wine_type == "sparkling" else 0
            is_white = 1 if wine_type == "white" else 0
            return [
                int(data["body"]),
                float(data["abv"]),
                is_rose,
                is_sparkling,
                is_white,
                int(data["dryness"])
            ]
        except jsonschema.ValidationError as ve:
            raise ValueError(f"Schema validation error: {ve.message}")
        except Exception as e:
            raise ValueError(f"Invalid input: {str(e)}")
    
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
