#!/bin/bash

# Start DRA Platform Backend on port 8001

echo "Starting DRA Platform Backend on port 8001..."
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
