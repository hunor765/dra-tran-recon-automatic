#!/bin/bash
set -e

# Railway sets PORT environment variable
# Default to 8000 if not set
PORT="${PORT:-8000}"

echo "Starting DRA Platform API..."
echo "Port: $PORT"
echo "Environment: $ENVIRONMENT"

# Verify ENCRYPTION_KEY is set
if [ -z "$ENCRYPTION_KEY" ]; then
    echo "ERROR: ENCRYPTION_KEY environment variable is not set!"
    exit 1
fi

# Run uvicorn with proper binding
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers 2 \
    --timeout-keep-alive 75 \
    --access-log
