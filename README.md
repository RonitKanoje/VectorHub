# ThreadCore

ThreadCore is a multi-user AI knowledge system for ingesting YouTube links, text, audio, and video, turning them into embeddings, and chatting against that content.

## Architecture

The project uses a MERN + FastAPI split:

- **apps/client** — React + Vite frontend (JWT stored in memory/httpOnly cookie)
- **apps/server** — Express + Node.js; owns authentication (bcrypt + JWT), proxies all AI requests to FastAPI
- **apps/api** — FastAPI entrypoint; internal-only, never exposed to the public internet
- **threadcore/** — Python AI core: chat graph, ingestion pipeline, media processing, vector store

Authentication flow: React → Express (JWT verify) → FastAPI (X-User-Id header) → AI services.

## Project Layout

```text
apps/
  api/                # FastAPI entrypoint (internal only)
  client/             # React + Vite UI
  server/             # Express auth + proxy server
threadcore/
  api/                # FastAPI routers, schemas, dependencies
  core/               # Settings
  infrastructure/     # Postgres, Redis, and Qdrant adapters
  services/           # Chat, ingestion, and media processing logic
data/
  runtime/            # Temporary uploaded/generated files
  samples/            # Sample media and debug payloads
docs/                 # Architecture and structure notes
scripts/
  debug/              # Ad hoc inspection/debug helpers
tests/                # Test package
```

## Run

### FastAPI (internal)

```bash
uvicorn apps.api.main:app --reload --port 8000
```

### Express server

```bash
cd apps/server
npm install
npm run dev
```

### React client

```bash
cd apps/client
npm install
npm run dev
```

## Environment

### Python (`/.env`)

Create from `.env.example`. Provide credentials for PostgreSQL, Redis, Qdrant, LangSmith, and Ollama.

### Node (`/apps/server/.env`)

```
PORT=<express-port>
THREADCORE_URL=<threadcore-internal-url>
CLIENT_URL=<client-origin>
GOOGLE_OAUTH_CALLBACK_URL=<public-api-origin>/api/auth/google/callback
JWT_SECRET=replace-me
JWT_EXPIRES_IN=7d
DATABASE_URL=postgresql://<db-user>:<db-password>@<db-host>:<db-port>/<db-name>
```

## Security model

FastAPI must listen on a private internal URL configured through `THREADCORE_URL` and trusts the `X-User-Id` header set by Express. **Never expose the FastAPI service to the public internet.** All public traffic goes through Express on the configured `PORT`.
