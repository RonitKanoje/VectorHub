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

COPY --chown=node:node apps/server/package*.json ./

RUN npm ci --omit=dev

COPY --chown=node:node --from=builder /app/dist ./dist

USER node

EXPOSE 3000

CMD ["node", "dist/server.js"]