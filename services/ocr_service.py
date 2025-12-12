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

from google.cloud import vision


class OCRService:
    """Service for optical character recognition using Google Cloud Vision API."""
    
    def __init__(self):
        """Initialize the OCR service with Vision API client."""
        self.vision_client = vision.ImageAnnotatorClient()
    
    def extract_text_from_image(self, image_content: bytes) -> str:
        """
        Extract text from an image using Google Cloud Vision API.
        
        Args:
            image_content: Binary content of the image
            
        Returns:
            Extracted text from the image
            
        Raises:
            Exception: If Vision API encounters an error
        """
        # Create Vision API image object
        image = vision.Image(content=image_content)
        
        # Perform text detection
        response = self.vision_client.text_detection(image=image)
        texts = response.text_annotations
        
        if response.error.message:
            raise Exception(f'Vision API error: {response.error.message}')
        
        # Extract full text (first annotation contains all text)
        if texts:
            return texts[0].description
        else:
            return ""
