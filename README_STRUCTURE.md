# Wine Recommender - Code Structure

## Overview
This application has been restructured following best practices for Flask applications with a clean, modular architecture.

## Directory Structure

```
wines-recommender/
├── app.py                  # Application entry point
├── app_factory.py          # Flask app factory
├── config.py               # Configuration with environment variable support
├── .env.example            # Example environment variables
├── routes/                 # HTTP route handlers (blueprints)
│   ├── __init__.py
│   ├── wine_routes.py      # Wine recommendation endpoints
│   └── ocr_routes.py       # OCR endpoints
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── wine_service.py     # Wine vector search logic
│   └── ocr_service.py      # OCR processing logic
├── schemas/                # Data validation schemas
│   ├── __init__.py
│   └── wine_schema.py      # Wine data JSON schema
└── utils/                  # Utility modules
    ├── logging.py          # Logging configuration
    └── metadata.py         # GCP metadata helpers
```

## Key Improvements

### 1. **Separation of Concerns**
- **Routes** (`routes/`): Handle HTTP requests/responses
- **Services** (`services/`): Contain business logic
- **Schemas** (`schemas/`): Define data validation rules
- **Config** (`config.py`): Centralized configuration

### 2. **Application Factory Pattern**
- `app_factory.py` creates and configures the Flask app
- Enables easier testing and multiple app instances
- Dependency injection for services

### 3. **Environment-Based Configuration**
- Support for environment variables
- `.env.example` file for documentation
- Default values for local development

### 4. **Blueprint-Based Routing**
- Routes organized by feature domain
- Clean URL prefixes (`/wines`, `/ocr`)
- Better code organization and maintainability

### 5. **Service Layer**
- `WineService`: Handles wine vector search and normalization
- `OCRService`: Manages image text extraction
- Services are testable independently from routes

### 6. **Better Error Handling & Logging**
- Structured logging throughout
- Consistent error responses
- Better debugging information

## Usage

### Running the Application

```bash
# Development
python app.py

# Production (with gunicorn)
gunicorn app:app
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### API Endpoints

#### POST /wines
Find similar wines based on characteristics.

**Request:**
```json
{
  "type": "Red",
  "body": 4,
  "dryness": 3,
  "abv": 13.5
}
```

**Response:**
```json
{
  "wines": ["wine_id_1", "wine_id_2"],
  "scores": {
    "wine_id_1": 0.95,
    "wine_id_2": 0.87
  }
}
```

#### POST /ocr
Extract text from wine label images.

**Request:**
- Multipart form data with `image` file

**Response:**
```json
{
  "text": "Extracted text from image"
}
```

#### GET /
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "wine-recommender"
}
```

## Testing

The modular structure makes testing easier:

```python
# Test services independently
from services import WineService

# Test routes with mocked services
# See test/ directory for examples
```

## Future Enhancements

Consider adding:
- `models/` directory for data models/classes
- `middleware/` for request/response processing
- `exceptions/` for custom exception classes
- `validators/` for additional validation logic
- Database models if needed
- API versioning (e.g., `/api/v1/wines`)
