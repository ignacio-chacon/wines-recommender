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

import signal
import sys
from types import FrameType

from flask import Flask, request, jsonify

# Add imports for Vertex AI Matching Engine
from google.cloud import aiplatform_v1

import jsonschema

from utils.logging import logger
from config import API_ENDPOINT, INDEX_ENDPOINT, DEPLOYED_INDEX_ID

# Configure Vector Search client
vector_search_client = aiplatform_v1.MatchServiceClient(client_options={"api_endpoint": API_ENDPOINT})

app = Flask(__name__)

SCHEMA = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": {
      "type": "string",
      "enum": ["Red", "White", "Rose", "Sparkling"]
    },
    "body": {
      "type": "integer",
      "minimum": 1,
      "maximum": 5
    },
    "dryness": {
      "type": "integer",
      "minimum": 1,
      "maximum": 5
    },
    "abv": {
      "type": "number"
    }
  },
  "required": ["type", "body", "dryness", "abv"],
}

def parse_wine_vector(data):
    try:
        jsonschema.validate(instance=data, schema=SCHEMA)
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

@app.route("/wines", methods=["POST"])
def get_wine_neighbors():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body."}), 400
    try:
        wine_vector = parse_wine_vector(data)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    # Build FindNeighborsRequest object
    datapoint = aiplatform_v1.IndexDatapoint(feature_vector=wine_vector)
    query = aiplatform_v1.FindNeighborsRequest.Query(datapoint=datapoint, neighbor_count=10)
    request_obj = aiplatform_v1.FindNeighborsRequest(
        index_endpoint=INDEX_ENDPOINT,
        deployed_index_id=DEPLOYED_INDEX_ID,
        queries=[query],
        return_full_datapoint=False,
    )
    try:
        response = vector_search_client.find_neighbors(request_obj)
        wine_neighbors = []
        distances = []
        
        # Collect all neighbors and distances
        for neighbor in response.nearest_neighbors[0].neighbors:
            datapoint_id = neighbor.datapoint.datapoint_id
            wine_neighbors.append(datapoint_id)
            distances.append(neighbor.distance)
        
        # Normalize distances to 0-1 scores using min-max normalization
        # Higher dot product = more similar, so we want higher scores for higher distances
        if distances:
            min_dist = min(distances)
            max_dist = max(distances)
            scores = {}
            if max_dist > min_dist:
                for wine_id, dist in zip(wine_neighbors, distances):
                    scores[wine_id] = (dist - min_dist) / (max_dist - min_dist)
            else:
                # All distances are the same
                for wine_id in wine_neighbors:
                    scores[wine_id] = 1.0
        else:
            scores = {}
            
        return jsonify({"wines": wine_neighbors, "scores": scores})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    from utils.logging import flush

    flush()

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
