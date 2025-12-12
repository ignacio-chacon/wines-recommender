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
from services import OCRService
from utils.logging import logger

ocr_bp = Blueprint('ocr', __name__, url_prefix='/ocr')


def create_ocr_routes(ocr_service: OCRService):
    """
    Create OCR-related routes with dependency injection.
    
    Args:
        ocr_service: Initialized OCRService instance
    """
    
    @ocr_bp.route("", methods=["POST"])
    def extract_text_from_image():
        """
        Extract text from an uploaded image using OCR.
        
        Request should contain:
        - image: Image file in multipart/form-data
        
        Returns:
            JSON response with extracted text
        """
        # Check if image is in request
        if 'image' not in request.files:
            logger.warning("OCR request missing image file")
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            logger.warning("OCR request with empty filename")
            return jsonify({"error": "No image file selected"}), 400
        
        try:
            # Read image content
            image_content = image_file.read()
            logger.info("Processing OCR request", extra={"image_size": len(image_content)})
            
            extracted_text = ocr_service.extract_text_from_image(image_content)
            logger.info("OCR extraction successful", extra={"text_length": len(extracted_text)})
            
            return jsonify({"text": extracted_text})
        except Exception as e:
            logger.error("OCR extraction failed", extra={"error": str(e)})
            return jsonify({"error": str(e)}), 500
    
    return ocr_bp
