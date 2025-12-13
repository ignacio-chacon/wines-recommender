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

from flask import Flask
from google.cloud import aiplatform_v1

import config
from services import WineService, OCRService, ModelService
from routes.wine_routes import create_wine_routes
from routes.ocr_routes import create_ocr_routes
from utils.logging import logger


def create_app() -> Flask:
    """
    Application factory pattern for creating and configuring the Flask app.
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config)
    
    logger.info("Initializing Wine Recommender application")
    
    # Initialize Vector Search client
    vector_search_client = aiplatform_v1.MatchServiceClient(
        client_options={"api_endpoint": config.API_ENDPOINT}
    )
    logger.info("Vector Search client initialized", extra={"api_endpoint": config.API_ENDPOINT})
    
    # Initialize Model Service for Two Tower Model
    model_service = None
    if config.MODEL_ENDPOINT or config.MODEL_ENDPOINT_ID:
        try:
            model_service = ModelService()
            logger.info("Model service initialized for Two Tower Model")
        except Exception as e:
            logger.warning(
                "Failed to initialize Model service, will use legacy mode",
                extra={"error": str(e)}
            )
    else:
        logger.info("Model endpoint not configured, running in legacy mode")
    
    # Initialize services
    wine_service = WineService(vector_search_client, model_service)
    ocr_service = OCRService()
    logger.info("Services initialized", extra={"model_enabled": model_service is not None})
    
    # Register blueprints with dependency injection
    app.register_blueprint(create_wine_routes(wine_service))
    app.register_blueprint(create_ocr_routes(ocr_service))
    logger.info("Routes registered")
    
    @app.route("/", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "wine-recommender"}, 200
    
    return app
