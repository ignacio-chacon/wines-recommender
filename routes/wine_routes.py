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

from flask import Blueprint, request, jsonify
from services import WineService
from utils.logging import logger

wine_bp = Blueprint('wines', __name__, url_prefix='/wines')


def create_wine_routes(wine_service: WineService):
    """
    Create wine-related routes with dependency injection.
    
    Args:
        wine_service: Initialized WineService instance
    """
    
    @wine_bp.route("", methods=["POST"])
    @wine_bp.route("/recommend", methods=["POST"])
    def get_wine_recommendations():
        """
        Get wine recommendations based on user preferences using the Two Tower Model.
        
        Request body should contain:
        - 55 user preference features (see USER_FEATURE_NAMES)
        - user_id: (optional) User ID (GUID) for tracking
        
        Returns:
            JSON response with wine IDs and similarity scores
        """
        data = request.get_json()
        if not data:
            logger.warning("Wine recommendation request missing body")
            return jsonify({"error": "Missing request body."}), 400
        
        try:
            # Extract optional user_id from the request
            user_id = data.get("user_id")
            
            # Use the Two Tower Model approach
            wine_ids, scores = wine_service.get_wine_recommendations(data, user_id=user_id)
            logger.info("Wine recommendations generated", extra={"count": len(wine_ids), "user_id": user_id})
            return jsonify({"wines": wine_ids, "scores": scores})
        except ValueError as ve:
            logger.error("User preferences validation failed", extra={"error": str(ve)})
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            logger.error("Wine recommendation failed", extra={"error": str(e)})
            return jsonify({"error": str(e)}), 500
    
    @wine_bp.route("/legacy", methods=["POST"])
    def get_wine_neighbors_legacy():
        """
        [DEPRECATED] Find similar wines using legacy direct vector conversion.
        
        This endpoint is kept for backward compatibility but should not be used
        for new implementations. Use /wines or /wines/recommend instead.
        
        Request body should contain:
        - type: Wine type (Red, White, Rose, Sparkling)
        - body: Body score (1-5)
        - dryness: Dryness score (1-5)
        - abv: Alcohol by volume percentage
        
        Returns:
            JSON response with wine IDs and similarity scores
        """
        data = request.get_json()
        if not data:
            logger.warning("Wine search request missing body")
            return jsonify({"error": "Missing request body."}), 400
        
        try:
            wine_vector = wine_service.parse_wine_vector(data)
            logger.info("Wine vector parsed successfully (legacy)", extra={"vector_length": len(wine_vector)})
        except ValueError as ve:
            logger.error("Wine vector validation failed", extra={"error": str(ve)})
            return jsonify({"error": str(ve)}), 400
        
        try:
            wine_neighbors, scores = wine_service.find_similar_wines(wine_vector)
            logger.info("Wine neighbors found (legacy)", extra={"count": len(wine_neighbors)})
            return jsonify({"wines": wine_neighbors, "scores": scores})
        except Exception as e:
            logger.error("Wine search failed", extra={"error": str(e)})
            return jsonify({"error": str(e)}), 500
    
    return wine_bp
