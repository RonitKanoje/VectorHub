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
    ffmpeg \
    # Required by opencv-python (cv2), docling, and docling-ibm-models (tableformer).
    # python:3.11-slim strips these OpenGL/GLib runtime libraries that are present
    # on every standard Linux install but absent from the minimal Docker base image.
    # libgl1       → provides libGL.so.1  (OpenGL runtime, linked by cv2)
    # libglib2.0-0 → provides libglib-2.0.so.0 (GLib, linked by cv2 and GTK layer)
    libgl1 \
    libglib2.0-0 \
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

# Create runtime directories BEFORE Docker mounts the volume
RUN mkdir -p \
    /app/data/runtime/uploads \
    /app/data/samples \
 && chown -R appuser:appuser /app

USER appuser

# Expose Port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "ai.api.app:app", "--host", "0.0.0.0", "--port", "8000"]