# ThreadCore Structure Guide

## What Changed

The repo previously mixed API code, chat logic, media processing, storage access, temp files, sample assets, and scratch scripts at the same level. The new layout separates those concerns so the project is easier to maintain and scale.

## Folder Responsibilities

### `apps/`

- `apps/api/main.py`
  Thin FastAPI startup entrypoint.
- `apps/streamlit/Home.py`
  Login and signup entrypoint for the Streamlit app.
- `apps/streamlit/pages/01_Chat.py`
  Main chat/upload experience.

### `threadcore/`

- `threadcore/api/`
  FastAPI-facing code: schemas, route modules, dependency helpers, and app assembly.
- `threadcore/core/`
  Shared config and authentication/security utilities.
- `threadcore/infrastructure/`
  External system adapters for Redis, PostgreSQL, and Qdrant.
- `threadcore/services/`
  Business logic for ingestion, media conversion/transcription, and chat orchestration.
- `threadcore/ui/`
  UI-only shared helpers such as Whisper language labels.

### `data/`

- `data/runtime/`
  Temporary uploads and generated runtime files. This should not be committed.
- `data/samples/`
  Sample media and JSON debug payloads that help development without polluting source folders.

### `scripts/`

- `scripts/debug/`
  One-off inspection scripts moved out of the main application package.

### `docs/`

- Documentation about architecture and project structure.

## Old-to-New Mapping

| Old path | Purpose | New location |
| --- | --- | --- |
| `api/app.py` | FastAPI app and routes | `threadcore/api/` + `apps/api/main.py` |
| `api/schemas.py` | Pydantic request/response models | `threadcore/api/schemas.py` |
| `backend/main.py` | Ingestion pipeline | `threadcore/services/ingestion/pipeline.py` |
| `backend/processing_chunks.py` | Chunk-to-document conversion | `threadcore/services/ingestion/chunking.py` |
| `backend/textbackend/app.py` | Text splitter | `threadcore/services/media/text.py` |
| `backend/videobackend/process_video.py` | Video/audio transcription helpers | `threadcore/services/media/video.py` |
| `backend/ytBackend/app.py` | YouTube transcript fetcher | `threadcore/services/media/youtube.py` |
| `backend/status.py` | Redis connection | `threadcore/infrastructure/cache/redis_client.py` |
| `chatbot/chatbot.py` | LangGraph chatbot flow | `threadcore/services/chat/graph.py` |
| `chatbot/nameChat.py` | Title generation | `threadcore/services/chat/naming.py` |
| `chatbot/prompt.py` | Prompt templates | `threadcore/services/chat/prompts.py` |
| `database/postgres/*` | Postgres access and models | `threadcore/infrastructure/db/` |
| `database/qdrant/*` | Chat embedding storage/retrieval | `threadcore/infrastructure/vector/` |
| `database/qdrantLongTerm/*` | Long-term memory storage/retrieval | `threadcore/infrastructure/vector/long_term_memory.py` |
| `frontend/login.py` | Streamlit auth screen | `apps/streamlit/Home.py` |
| `frontend/pages/app.py` | Streamlit chat page | `apps/streamlit/pages/01_Chat.py` |
| `frontend/pages/languages.py` | Whisper language options | `threadcore/ui/streamlit/languages.py` |
| `utils/hashing.py` | Password hashing | `threadcore/core/security.py` |
| `utils/jwt_handler.py` | JWT auth helpers | `threadcore/core/security.py` |
| `chatbot/check.py` | Env/debug script | `scripts/debug/chatbot_env_check.py` |
| `chatbot/Untitled-1.py` | Conversation snapshot scratch file | `scripts/debug/conversation_snapshot.py` |
| `database/qdrant/check.py` | Qdrant inspection script | `scripts/debug/qdrant_check.py` |
| `docs.json`, `docs2.json`, `merge.json` | Sample/debug data | `data/samples/` |
| `backend/videobackend/tmp/*` | Runtime uploads | `data/runtime/uploads/` |
| `backend/videobackend/*.mp4`, `audios/output.mp3` | Sample media | `data/samples/media/` |

## Why This Is Closer To Production

- Application code lives in one package instead of several unrelated top-level folders.
- Entry points are separate from business logic.
- Runtime files no longer sit inside source directories.
- External systems are isolated behind infrastructure modules.
- Scratch/debug files are clearly marked and separated from deployable code.

