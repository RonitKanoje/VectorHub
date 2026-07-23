# Build Stage only — static files are served by the central Nginx container.
# See nginx/Dockerfile for the full multi-stage build that consumes this output.
FROM node:22-alpine AS builder

WORKDIR /app

# Declare the build argument (passed from docker-compose build.args)
ARG VITE_API_BASE_URL
# Expose it as an environment variable so Vite can read it during build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY apps/client/package*.json ./

RUN npm ci

COPY apps/client .

RUN npm run build