#!/bin/bash
# Script to run the TRIWA Image API

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "uvicorn is not installed. Installing dependencies..."
    uv pip install -e .
fi

# Run the FastAPI application
echo "Starting TRIWA Image API..."
uvicorn app:app --reload --host 0.0.0.0 --port 8000 