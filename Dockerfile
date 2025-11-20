# AI Trend Monitor - Dockerfile for Railway deployment
# 
# This Dockerfile is used to deploy the FastAPI backend to Railway.
# It supports both API server and Worker process deployment.

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.5

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (without dev dependencies)
RUN poetry install --no-dev && rm -rf $POETRY_CACHE_DIR

# Add Poetry virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY backend/ ./backend/
# alembic.ini and alembic/ are already included in backend/ directory

# Expose port (Railway will set PORT environment variable)
EXPOSE 8000

# Default command (can be overridden in Railway settings)
# For API server: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
# For Worker: python -m backend.scripts.worker
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

