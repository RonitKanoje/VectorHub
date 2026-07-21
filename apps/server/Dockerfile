# Build Stage
FROM node:22-alpine AS builder

WORKDIR /app

COPY apps/server/package*.json ./

RUN npm ci

COPY apps/server .

RUN npm run build

# Runtime Stage
FROM node:22-alpine

WORKDIR /app

COPY apps/server/package*.json ./

RUN npm ci --omit=dev

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["node", "dist/server.js"]