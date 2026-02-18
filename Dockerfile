FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements
COPY apps/platform/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY apps/platform/backend/ .

# Expose port
EXPOSE 8000

# Use ENTRYPOINT with shell form to support env vars
ENTRYPOINT ["sh", "-c"]
CMD ["uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
