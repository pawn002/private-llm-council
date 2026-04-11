# The Sovereign Council - Backend
# Privacy-first local LLM council API

FROM python:3.11-slim AS base

# Security: run as non-root user
RUN useradd --create-home --shell /bin/bash council
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY backend/pyproject.toml .
COPY backend/src/__init__.py src/
COPY README.md ../README.md

# Install Python dependencies (including dev extras for pytest/probe scripts)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[dev]"

# Copy application code
COPY backend/src/ src/

# Copy test suite and probe scripts (volume-mounted in docker-compose for live edits)
COPY backend/tests/ tests/
COPY backend/scripts/ scripts/

# Create data directory for persistent storage
RUN mkdir -p /app/data && chown -R council:council /app

# Switch to non-root user
USER council

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Environment
ENV PYTHONUNBUFFERED=1
ENV SOVEREIGN_COUNCIL_DATA_DIR=/app/data

# Default port
EXPOSE 8000

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--timeout-keep-alive", "1800", \
     "--timeout-graceful-shutdown", "30"]
