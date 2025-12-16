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

import json
from typing import Dict, List, Optional
from google.cloud import storage
from utils.logging import logger


class EmbeddingsService:
    """Service for loading and managing wine embeddings in memory."""

    def __init__(self, gcs_uri: str = "gs://wines_bucket/wine-embeddings/embeddings_20251216_003124.json"):
        """
        Initialize the embeddings service.

        Args:
            gcs_uri: GCS URI of the embeddings file
        """
        self.gcs_uri = gcs_uri
        self.embeddings: Dict[str, List[float]] = {}
        self._load_embeddings()

    def _load_embeddings(self):
        """Load wine embeddings from GCS into memory."""
        logger.info("Loading wine embeddings from GCS", extra={"uri": self.gcs_uri})

        try:
            # Parse GCS URI
            if not self.gcs_uri.startswith("gs://"):
                raise ValueError(f"Invalid GCS URI: {self.gcs_uri}")

            path_parts = self.gcs_uri[5:].split("/", 1)
            bucket_name = path_parts[0]
            blob_name = path_parts[1]

            # Download from GCS
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Download as string and parse JSON lines
            content = blob.download_as_text()

            count = 0
            for line in content.strip().split('\n'):
                if line:
                    entry = json.loads(line)
                    wine_id = str(entry['id'])
                    embedding = entry['embedding']
                    self.embeddings[wine_id] = embedding
                    count += 1

            logger.info(
                "Wine embeddings loaded successfully",
                extra={
                    "total_wines": count,
                    "memory_size_mb": len(content) / (1024 * 1024)
                }
            )
        except Exception as e:
            logger.error(
                "Failed to load wine embeddings",
                extra={"error": str(e), "uri": self.gcs_uri}
            )
            raise Exception(f"Failed to load embeddings: {str(e)}")

    def get_embedding(self, wine_id: str) -> Optional[List[float]]:
        """
        Get embedding for a specific wine (O(1) lookup).

        Args:
            wine_id: Wine ID as string

        Returns:
            Wine embedding vector or None if not found
        """
        return self.embeddings.get(wine_id)

    def get_embeddings(self, wine_ids: List[str]) -> Dict[str, List[float]]:
        """
        Get embeddings for multiple wines (O(n) where n = number of wine_ids).

        Args:
            wine_ids: List of wine IDs

        Returns:
            Dictionary mapping wine IDs to embeddings (only for found wines)
        """
        result = {}
        for wine_id in wine_ids:
            embedding = self.get_embedding(wine_id)
            if embedding is not None:
                result[wine_id] = embedding

        logger.info(
            "Retrieved embeddings",
            extra={
                "requested": len(wine_ids),
                "found": len(result),
                "missing": len(wine_ids) - len(result)
            }
        )

        return result

    def has_embedding(self, wine_id: str) -> bool:
        """Check if embedding exists for a wine."""
        return wine_id in self.embeddings

    def get_total_count(self) -> int:
        """Get total number of wines with embeddings."""
        return len(self.embeddings)
