from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from threadcore.api.routes.chat import router as chat_router
from threadcore.api.routes.ingestion import router as ingestion_router
from threadcore.api.routes.threads import router as threads_router
from threadcore.core.config import settings
from threadcore.infrastructure.cache.redis_client import is_redis_available
from threadcore.infrastructure.db.checkpointer import get_checkpointer
from threadcore.infrastructure.db.models import init_db
from threadcore.services.chat.graph import build_chatbot
from threadcore.services.analyst.graph import build_analyst_app

## before accepting anything just run this code 
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_runtime_directories()
    init_db()
    app.state.checkpointer, app.state.pool = await get_checkpointer()
    app.state.chatbot = build_chatbot(app.state.checkpointer)
    app.state.analyst_app = build_analyst_app(app.state.checkpointer)
    is_redis_available()
    yield
    await app.state.pool.close()


app = FastAPI(title="ThreadCore API", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    errors = exc.errors()
    message = "; ".join(
        f"{'.'.join(str(part) for part in error.get('loc', ['request']))}: {error.get('msg')}"
        for error in errors
    )
    print(
        "Request validation failed",
        {
            "method": request.method,
            "path": request.url.path,
            "errors": errors,
            "body": body.decode("utf-8", errors="replace"),
            "has_x_user_id": bool(request.headers.get("X-User-Id")),
        },
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

from threadcore.api.routes.dataset import router as dataset_router

app.include_router(chat_router)
app.include_router(ingestion_router)
app.include_router(dataset_router)
app.include_router(threads_router)
