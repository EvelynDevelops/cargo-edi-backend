# Cargo EDI Backend

This is the backend service for the Cargo EDI application, which handles EDI message validation, parsing, and generation.

## Features

- EDI message validation with detailed error reporting
- EDI message parsing into structured data
- EDI message generation from structured data
- Logging for debug, info, and error messages

## Technology Stack

- Python 3.9+
- FastAPI
- Pydantic

## Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- virtualenv (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cargo-edi-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode

Start the backend server in development mode:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Production Mode

For production, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## API Endpoints

### 1. Decode EDI Message

**Endpoint:** `POST /decode-edi`

**Request Body:**
```json
{
  "edi": "LIN+1+I'\nPAC+++LCL:67:95'\nPAC+9+1'\nPCI+1'\nRFF+AAQ:ABC123'\nPCI+1'\nRFF+MB:DEF456'\nPCI+1'\nRFF+BH:GHI789'"
}
```

**Response:**
```json
{
  "cargo_items": [
    {
      "cargo_type": "LCL",
      "number_of_packages": 9,
      "container_number": "ABC123",
      "master_bill_of_lading_number": "DEF456",
      "house_bill_of_lading_number": "GHI789"
    }
  ],
  "logs": [
    "2023-12-01 12:00:00 - INFO - Starting EDI decode. Total lines: 9",
    "2023-12-01 12:00:00 - INFO - EDI passed validation",
    "2023-12-01 12:00:00 - INFO - EDI decoding completed. Total cargo items: 1"
  ]
}
```

### 2. Generate EDI Message

**Endpoint:** `POST /generate-edi`

**Request Body:**
```json
{
  "cargo_items": [
    {
      "cargo_type": "LCL",
      "number_of_packages": 9,
      "container_number": "ABC123",
      "master_bill_of_lading_number": "DEF456",
      "house_bill_of_lading_number": "GHI789"
    }
  ]
}
```

**Response:**
```json
{
  "edi": "LIN+1+I'\nPAC+++LCL:67:95'\nPAC+9+1'\nPCI+1'\nRFF+AAQ:ABC123'\nPCI+1'\nRFF+MB:DEF456'\nPCI+1'\nRFF+BH:GHI789'"
}
```

## Data Model

### CargoItem

```python
class CargoItem(BaseModel):
    cargo_type: str                               # LCL, FCL, etc.
    number_of_packages: int                       # Number of packages
    cargo_name: Optional[str] = None              # Description of cargo
    container_number: Optional[str] = None        # Container number
    master_bill_of_lading_number: Optional[str] = None  # Master B/L number
    house_bill_of_lading_number: Optional[str] = None   # House B/L number
```

## EDI Format Rules

The backend validates EDI messages according to the following rules:

1. Each cargo item must start with a LIN segment.
2. Each cargo item must contain PAC+++{cargo type}:67:95', PAC+{number}+1'.
3. RFF+AAQ, RFF+MB, RFF+BH are optional but must be preceded by PCI+1'.
4. PCI+1' must not appear without a corresponding RFF line.
5. RFF+AAQ:, RFF+MB:, RFF+BH: values must contain only letters and numbers.
6. No empty lines are allowed between EDI segments.
7. PAC+{number}+1' number must be a positive integer.
8. Each line must end with a single quote (').
9. Cargo name must follow specific format (uppercase or sentence case, spaces, hyphens and numbers allowed).

## Logging

The application uses a comprehensive logging system that captures:

- Debug information
- Validation steps
- Parsing details
- Error messages

Logs are returned with API responses for easier debugging.

## Development

### Project Structure

```
cargo-edi-backend/
├── api/                   # API routes
│   ├── decode_edi_route.py
│   └── generate_edi_route.py
├── services/              # Business logic
│   ├── edi_decoder.py     # EDI parsing
│   ├── edi_validator.py   # EDI validation
│   └── edi_generator.py   # EDI generation
├── funcs/                 # Utility functions
│   └── utils/
│       └── edi_logging.py # Logging utilities
├── main.py                # Application entry point
└── requirements.txt       # Dependencies
```

### Running Tests

```bash
pytest
```

## Troubleshooting

### Common Issues

1. **Validation Errors**: Ensure your EDI follows the format rules described above.
2. **Missing Dependencies**: Make sure all requirements are installed.
3. **Port Already in Use**: Change the port in the run command if 8000 is already in use.

## License

[License information]

## Contact

For questions or support, please contact [contact information].
