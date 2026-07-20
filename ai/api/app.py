import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ai.infrastructure.db.session import configure_asyncio_for_windows
from ai.api.routes.chat import router as chat_router
from ai.api.routes.ingestion import router as ingestion_router
from ai.api.routes.threads import router as threads_router
from ai.core.config import settings
from ai.infrastructure.cache.redis_client import is_redis_available
from ai.infrastructure.db.checkpointer import get_checkpointer
from ai.infrastructure.db.models import init_db
from ai.services.chat.graph import build_chatbot
from ai.services.analyst.graph import build_analyst_app
from ai.api.routes.dataset import router as dataset_router
from ai.api.routes.analyst import router as analyst_router

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.DEBUG),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

configure_asyncio_for_windows()

## before accepting anything just run this code 
@asynccontextmanager
async def lifespan(app: FastAPI): ## newer version of fastapi uses lifespan instead of startup and shutdown events
    settings.ensure_runtime_directories()
    init_db()
    app.state.checkpointer, app.state.pool = await get_checkpointer()
    app.state.chatbot = build_chatbot(app.state.checkpointer)
    app.state.analyst_app = build_analyst_app(app.state.checkpointer)
    is_redis_available()
    yield
    if getattr(app.state, "pool", None) is not None: ## closing the pool of connections to the database when the application is shutting down
        await app.state.pool.close()


app = FastAPI(title="AI API", lifespan=lifespan)

## Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    errors = exc.errors()
    message = "; ".join(
        f"{'.'.join(str(part) for part in error.get('loc', ['request']))}: {error.get('msg')}"
        for error in errors
    )
    return JSONResponse(
        status_code=422,
        content={"detail": errors, "message": message or "Invalid request"},
    )


@app.get("/")
async def read_root():
    return {"status": "API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(chat_router)
app.include_router(ingestion_router)
app.include_router(dataset_router)
app.include_router(analyst_router)
app.include_router(threads_router)
