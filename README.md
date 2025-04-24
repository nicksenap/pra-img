# TRIWA Image API

A FastAPI application that processes a list of EANs and returns a CSV file with image URLs for TRIWA products.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
uv pip install -e .
```

## Running the API

```bash
uvicorn app:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### 1. Process EANs from a File

`POST /process-eans/`

Upload a text file containing one EAN per line. The API will return a CSV file with all image URLs.

Example using curl:
```bash
curl -X POST -F "file=@data/ean_list.txt" http://localhost:8000/process-eans/ -o triwa_images.csv
```

### 2. Process EANs from JSON

`POST /process-eans-text/`

Send a JSON array of EANs. The API will return a CSV file with all image URLs.

Example using curl:
```bash
curl -X POST -H "Content-Type: application/json" -d '["7350056808765", "7350056806419"]' http://localhost:8000/process-eans-text/ -o triwa_images.csv
```

## Documentation

API documentation is available at:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc
