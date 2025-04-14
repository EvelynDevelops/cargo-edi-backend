# Cargo EDI Backend

A FastAPI-based backend service for generating and decoding EDI (Electronic Data Interchange) messages for cargo shipments.

## Setup Instructions

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`

## System Requirements

- Python 3.8 or later
- pip (Python package manager)


## Key Dependencies

- FastAPI - Modern web framework
- Pydantic - Data validation
- Uvicorn - ASGI server
- pytest - Testing framework

## Development

### Running Tests
```bash
pytest
```

## Possible Improvements

### Testing
- Add more unit tests for services and utilities
- Add integration tests for API endpoints

### Features
- Add support for more EDI message types
- Add message validation against EDI standards

### Performance
- Optimize EDI message parsing
