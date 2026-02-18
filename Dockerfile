FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for psycopg2-binary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY apps/platform/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/platform/backend/ .

# Make start script executable
RUN chmod +x start.sh

# Railway dynamically assigns PORT
EXPOSE 8000

# Use the start script
CMD ["./start.sh"]
