# Architecture Overview

## Request Flow

```
Client Request
     |
     v
[app.py] ──────────> Entry Point & Signal Handlers
     |
     v
[app_factory.py] ──> Creates Flask App
     |              • Loads config
     |              • Initializes clients
     |              • Creates services
     |              • Registers blueprints
     |
     v
[routes/] ─────────> HTTP Layer (Blueprints)
     |              • wine_routes.py  → /wines
     |              • ocr_routes.py   → /ocr
     |
     v
[services/] ───────> Business Logic Layer
     |              • WineService    → Vector search logic
     |              • OCRService     → Image processing logic
     |
     v
[External APIs]
     • Google Cloud Vertex AI (Vector Search)
     • Google Cloud Vision API (OCR)
```

## Module Dependencies

```
app.py
  └─> app_factory.py
       ├─> config.py
       ├─> services/
       │    ├─> wine_service.py
       │    │    ├─> schemas/wine_schema.py
       │    │    └─> config.py
       │    └─> ocr_service.py
       └─> routes/
            ├─> wine_routes.py
            │    └─> services/wine_service.py
            └─> ocr_routes.py
                 └─> services/ocr_service.py
```

## Layer Responsibilities

### 1. Entry Layer (`app.py`)
- Application startup
- Signal handling (Ctrl+C, SIGTERM)
- Environment detection (local vs Cloud Run)

### 2. Factory Layer (`app_factory.py`)
- App initialization
- Dependency injection
- Blueprint registration
- Client configuration

### 3. Route Layer (`routes/`)
- HTTP request/response handling
- Input validation
- Error responses
- Logging

### 4. Service Layer (`services/`)
- Business logic
- Data transformation
- External API calls
- Algorithm implementation

### 5. Schema Layer (`schemas/`)
- Data validation rules
- JSON schema definitions
- Input contracts

### 6. Config Layer (`config.py`)
- Environment variables
- Default values
- Application settings

### 7. Utils Layer (`utils/`)
- Logging configuration
- GCP metadata helpers
- Shared utilities

## Design Patterns Used

1. **Application Factory Pattern**: `create_app()` for flexible app creation
2. **Dependency Injection**: Services injected into routes
3. **Blueprint Pattern**: Modular route organization
4. **Service Layer Pattern**: Business logic separation
5. **Configuration Pattern**: Environment-based config

## Benefits of This Architecture

### Testability
```python
# Test service independently
def test_wine_service():
    mock_client = Mock()
    service = WineService(mock_client)
    vector = service.parse_wine_vector({...})
    assert vector == expected

# Test route with mocked service
def test_wine_route():
    mock_service = Mock()
    app = create_test_app(wine_service=mock_service)
    response = app.test_client().post('/wines', ...)
    assert response.status_code == 200
```

### Maintainability
- Each file < 150 lines
- Clear separation of concerns
- Easy to locate and fix bugs
- Self-documenting structure

### Scalability
- Easy to add new endpoints (new blueprint)
- Easy to add new services
- Easy to add middleware
- Easy to version APIs

### Team Collaboration
- Developers can work on different modules
- Clear ownership boundaries
- Reduced merge conflicts
- Easier code reviews
