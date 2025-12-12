# Developer Quick Reference

## Adding a New Feature

### 1. Add a New Endpoint

**Step 1**: Create a service (if needed)
```python
# services/my_new_service.py
class MyNewService:
    def __init__(self, client):
        self.client = client
    
    def process(self, data):
        # Your business logic here
        return result
```

**Step 2**: Create routes
```python
# routes/my_new_routes.py
from flask import Blueprint, request, jsonify
from services import MyNewService

my_bp = Blueprint('myfeature', __name__, url_prefix='/myfeature')

def create_my_routes(my_service: MyNewService):
    @my_bp.route("", methods=["POST"])
    def my_endpoint():
        data = request.get_json()
        result = my_service.process(data)
        return jsonify(result)
    
    return my_bp
```

**Step 3**: Register in app factory
```python
# app_factory.py
from routes.my_new_routes import create_my_routes

def create_app():
    # ...
    my_service = MyNewService(client)
    app.register_blueprint(create_my_routes(my_service))
```

### 2. Add Configuration

```python
# config.py
MY_NEW_CONFIG = os.getenv("MY_NEW_CONFIG", "default_value")
```

```bash
# .env
MY_NEW_CONFIG=production_value
```

### 3. Add Schema Validation

```python
# schemas/my_schema.py
MY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "field": {"type": "string"}
    },
    "required": ["field"]
}
```

## Common Tasks

### Run Locally
```bash
python app.py
# or
python3 app.py
```

### Run with Gunicorn
```bash
gunicorn app:app --bind 0.0.0.0:8080
```

### Test Single Module
```bash
python -m pytest test/test_app.py -v
```

### Check Code Style
```bash
# Install tools
pip install black flake8 mypy

# Format code
black .

# Lint
flake8 .

# Type check
mypy .
```

### Environment Variables
```bash
# Development
cp .env.example .env
# Edit .env with your values

# Production
export API_ENDPOINT="your-endpoint"
export INDEX_ENDPOINT="your-index"
```

## File Templates

### New Service Template
```python
# services/new_service.py
from typing import Any, Dict
from utils.logging import logger

class NewService:
    """Description of the service."""
    
    def __init__(self, dependency):
        """Initialize with dependencies."""
        self.dependency = dependency
        logger.info("NewService initialized")
    
    def method(self, data: Dict[str, Any]) -> Any:
        """
        Method description.
        
        Args:
            data: Input data
            
        Returns:
            Processed result
            
        Raises:
            ValueError: If validation fails
        """
        logger.info("Processing request")
        # Implementation
        return result
```

### New Route Template
```python
# routes/new_routes.py
from flask import Blueprint, request, jsonify
from services import NewService
from utils.logging import logger

new_bp = Blueprint('new', __name__, url_prefix='/new')

def create_new_routes(service: NewService):
    """Create routes with dependency injection."""
    
    @new_bp.route("", methods=["POST"])
    def endpoint():
        """Endpoint description."""
        data = request.get_json()
        if not data:
            logger.warning("Missing request body")
            return jsonify({"error": "Missing body"}), 400
        
        try:
            result = service.method(data)
            logger.info("Request successful")
            return jsonify(result)
        except ValueError as e:
            logger.error("Validation error", extra={"error": str(e)})
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error("Processing error", extra={"error": str(e)})
            return jsonify({"error": str(e)}), 500
    
    return new_bp
```

## Debugging

### Enable Debug Mode
```bash
# In .env
DEBUG=true

# Or export
export DEBUG=true
```

### View Logs
```python
# In your code
from utils.logging import logger

logger.info("Info message", extra={"key": "value"})
logger.warning("Warning message")
logger.error("Error message", extra={"error": str(e)})
```

### Common Issues

**Import errors**: Check Python path and virtual environment
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

**Config not loading**: Check environment variables
```bash
python -c "import os; print(os.getenv('API_ENDPOINT'))"
```

**Routes not found**: Ensure blueprint is registered in `app_factory.py`

## Best Practices

1. **Always use type hints** for better IDE support
2. **Log at service layer** for debugging
3. **Validate at route layer** for security
4. **Keep services pure** (no Flask dependencies)
5. **Use dependency injection** for testability
6. **Document with docstrings** for clarity
7. **Handle errors gracefully** with proper status codes
8. **Use config for all settings** (no hardcoded values)

## Code Style

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Follow PEP 8 conventions
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused
