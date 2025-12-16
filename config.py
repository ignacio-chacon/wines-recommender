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

import os

# Flask Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "8080"))

# Vertex AI Vector Search Configuration
API_ENDPOINT = os.getenv(
    "API_ENDPOINT",
    "1173956.us-central1-438750044055.vdb.vertexai.goog"
)
INDEX_ENDPOINT = os.getenv(
    "INDEX_ENDPOINT",
    "projects/438750044055/locations/us-central1/indexEndpoints/174780567374528512"
)
DEPLOYED_INDEX_ID = os.getenv(
    "DEPLOYED_INDEX_ID",
    "deployed_index_20251216_003124"
)

# Wine Search Configuration
DEFAULT_NEIGHBOR_COUNT = int(os.getenv("DEFAULT_NEIGHBOR_COUNT", "10"))

# Two Tower Model Configuration
MODEL_ENDPOINT = os.getenv(
    "MODEL_ENDPOINT",
    ""  # e.g., "projects/PROJECT_ID/locations/REGION/endpoints/ENDPOINT_ID"
)
MODEL_PROJECT_ID = os.getenv("MODEL_PROJECT_ID", "enhanced-layout-465420-v5")
MODEL_LOCATION = os.getenv("MODEL_LOCATION", "us-central1")
MODEL_ENDPOINT_ID = os.getenv("MODEL_ENDPOINT_ID", "1904309059331293184")