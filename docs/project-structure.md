# ThreadCore Project Structure

## High-Level Architecture

ThreadCore is organized into three major applications:

```text
React Client
      │
      ▼
Express Gateway
      │
      ▼
FastAPI AI Backend
```

The frontend communicates with Express. Express handles authentication and authorization, then forwards trusted requests to FastAPI. FastAPI is responsible for AI, ingestion, retrieval, memory, and chat orchestration.

---

# Project Tree

```text
ThreadCore/
│
├── apps/                           # Application entry points
│   │
│   ├── client/                     # React Frontend
│   │   ├── pages
│   │   ├── components
│   │   ├── services/api
│   │   └── ...
│   │
│   ├── server/                     # Express Gateway
│   │   ├── routes
│   │   ├── middleware
│   │   ├── controllers
│   │   └── ...
│   │
│   └── api/
│       └── main.py                 # FastAPI startup
│
├── threadcore/                     # AI Backend
│   │
│   ├── api/                        # HTTP Layer
│   │   ├── app.py
│   │   ├── dependencies.py
│   │   ├── schemas.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── chat.py
│   │       ├── ingestion.py
│   │       └── threads.py
│   │
│   ├── core/                       # Shared Configuration
│   │   └── config.py
│   │
│   ├── infrastructure/             # External Systems
│   │   ├── cache/
│   │   │   └── redis_client.py
│   │   │
│   │   ├── db/
│   │   │   ├── models.py
│   │   │   ├── repositories.py
│   │   │   ├── session.py
│   │   │   └── checkpointer.py
│   │   │
│   │   └── vector/
│   │       ├── qdrant.py
│   │       ├── chat_embeddings.py
│   │       └── long_term_memory.py
│   │
│   └── services/                   # Business Logic
│       ├── chat/
│       │   ├── graph.py
│       │   ├── naming.py
│       │   └── prompts.py
│       │
│       ├── ingestion/
│       │   ├── pipeline.py
│       │   └── chunking.py
│       │
│       └── media/
│           ├── text.py
│           ├── video.py
│           └── youtube.py
│
├── data/
│   ├── runtime/
│   │   └── uploads/
│   │
│   └── samples/
│
├── scripts/
│   └── debug/
│       ├── chatbot_env_check.py
│       ├── conversation_snapshot.py
│       └── qdrant_check.py
│
├── tests/
│
└── docs/
```

---

# Layer Responsibilities

## 1. apps/

Contains application entry points.

### client/

React frontend responsible for:

* Login and signup UI
* Chat interface
* Media upload interface
* Thread management
* Calling Express APIs

### server/

Express gateway responsible for:

* User authentication
* JWT verification
* Password hashing
* Route protection
* Forwarding requests to FastAPI

### api/

FastAPI startup entrypoint.

Responsible for:

* Starting FastAPI
* Loading services
* Registering routes
* Initializing application lifecycle

---

## 2. threadcore/api/

HTTP layer of the AI backend.

### app.py

Builds and configures the FastAPI application.

### dependencies.py

Shared route dependencies.

Examples:

* get_current_user
* ensure_thread_access
* get_chatbot

### schemas.py

Pydantic request and response models.

### routes/

Defines API endpoints.

* auth.py
* chat.py
* ingestion.py
* threads.py

Routes should remain thin and delegate business logic to services.

---

## 3. threadcore/core/

Shared application configuration.

### config.py

Contains:

* Environment variables
* Runtime paths
* Application settings
* Service configuration

This layer is shared across the entire backend.

---

## 4. threadcore/services/

Contains business logic.

### chat/

Responsible for:

* LangGraph workflow
* Prompt construction
* Conversation management
* Title generation

### ingestion/

Responsible for:

* Processing uploaded content
* Chunking documents
* Creating embeddings
* Storing searchable knowledge

### media/

Responsible for:

* Video transcription
* Audio transcription
* YouTube transcript extraction
* Text processing

---

## 5. threadcore/infrastructure/

Contains integrations with external systems.

### cache/

Redis integration.

Used for:

* Upload status
* Processing state
* Temporary runtime information

### db/

PostgreSQL integration.

Contains:

* Database models
* Repositories
* Sessions
* LangGraph checkpointer

### vector/

Qdrant integration.

Contains:

* Embedding storage
* Similarity search
* Long-term memory retrieval

---

## 6. data/

Stores non-source-code data.

### runtime/

Temporary generated files.

Examples:

* Uploaded videos
* Audio files
* Intermediate transcripts

Should not be committed.

### samples/

Development assets.

Examples:

* Sample media
* Debug JSON payloads
* Test files

Safe to commit.

---

## 7. scripts/

Developer utilities.

Examples:

* Environment validation
* Qdrant inspection
* Conversation inspection

These are not part of the running application.

---

## 8. tests/

Contains:

* Unit tests
* Integration tests
* Future automated test suites

---

## 9. docs/

Project documentation.

Examples:

* Architecture diagrams
* API documentation
* Design decisions
* Development guides

---

# Request Flow

## Chat Request

```text
React Client
      │
      ▼
Express Gateway
      │
      ▼
FastAPI Route
      │
      ▼
Chat Service
      │
      ├── Postgres Checkpointer
      ├── Qdrant Retrieval
      └── Ollama
      │
      ▼
Response
```

---

## Media Upload

```text
React Client
      │
      ▼
Express Gateway
      │
      ▼
FastAPI Route
      │
      ▼
Ingestion Pipeline
      │
      ▼
Media Processing
      │
      ▼
Chunking
      │
      ▼
Embeddings
      │
      ▼
Qdrant
```

---

# Dependency Flow

A simple rule for the project:

```text
apps
  ↓
api
  ↓
services
  ↓
infrastructure
  ↓
external systems
```

Higher layers can depend on lower layers.

Lower layers should never depend on higher layers.

This keeps the architecture clean, maintainable, and scalable.
