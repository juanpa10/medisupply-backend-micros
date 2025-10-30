FROM python:3.11-slim

LABEL maintainer="MediSupply Team"
LABEL service="inventory-service"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    PORT=9008

# Expose port
# Expose the container port (aligned with host mapping)
EXPOSE 9008

# Normalize line endings and make entrypoint executable (fix CRLF on Windows hosts)
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9008/health', timeout=5)" || exit 1

# Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
