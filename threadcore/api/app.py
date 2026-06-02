from contextlib import asynccontextmanager

from fastapi import FastAPI

from threadcore.api.routes.chat import router as chat_router
from threadcore.api.routes.ingestion import router as ingestion_router
from threadcore.api.routes.threads import router as threads_router
from threadcore.core.config import settings
from threadcore.infrastructure.cache.redis_client import redis_client
from threadcore.infrastructure.db.checkpointer import get_checkpointer
from threadcore.infrastructure.db.models import init_db
from threadcore.services.chat.graph import build_chatbot


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_runtime_directories()
    init_db()
    app.state.checkpointer = get_checkpointer()
    app.state.chatbot = build_chatbot(app.state.checkpointer)
    try:
        redis_client.ping()
    except Exception:
        pass
    yield


app = FastAPI(title="ThreadCore API", lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"status": "API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(chat_router)
app.include_router(ingestion_router)
app.include_router(threads_router)
