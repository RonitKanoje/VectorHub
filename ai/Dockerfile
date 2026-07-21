# Base Image
FROM python:3.11-slim

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create Non-root User
RUN useradd --create-home appuser

# Working Directory
WORKDIR /app

# Install Python Dependencies
COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy AI Source Code
COPY ai ./ai

# Permissions
RUN chown -R appuser:appuser /app

USER appuser

# Expose Port
EXPOSE 8000

# Health Check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI
CMD ["uvicorn", "ai.api.app:app", "--host", "0.0.0.0", "--port", "8000"]