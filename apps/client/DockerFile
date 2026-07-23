# Build Stage
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

# Production Stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]