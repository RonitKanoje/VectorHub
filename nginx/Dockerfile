# ---------------------------------------------------------------
# Stage 1 — Build the React app
# ---------------------------------------------------------------
FROM node:22-alpine AS client-builder

WORKDIR /app

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY apps/client/package*.json ./
RUN npm ci

COPY apps/client .
RUN npm run build

# ---------------------------------------------------------------
# Stage 2 — Nginx reverse proxy
# ---------------------------------------------------------------
FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy the reverse proxy config
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy the compiled React static files from the builder
COPY --from=client-builder /app/dist /usr/share/nginx/html

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
