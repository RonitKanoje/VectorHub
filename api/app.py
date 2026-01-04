from fastapi import FastAPI, HTTPException, BackgroundTasks
from api.schemas import processMedia
from database.postgres.checkpointer import get_checkpointer
from langchain_core.messages import HumanMessage
from chatbot.chatbot import retrieve_all_threads, loadConv
import json
from backend.main import main
from chatbot.chatbot import build_chatbot
from api.schemas import processMedia,chatMessage
from backend.status import redis_client
from database.qdrant.vectorStore import create_vector_store
from fastapi import HTTPException
from langsmith import traceable

app = FastAPI()

@app.get("/")
async def read_root():
    return {"status": "API is running"}

@app.on_event("startup")
def startup():
    app.state.checkpointer = get_checkpointer()
    app.state.chatbot = build_chatbot(app.state.checkpointer)
    try:
        redis_client.ping()
        print("Connected to Redis successfully!")
    except Exception as e:
        print("Failed to connect to Redis:", e)

@traceable(name="ChatBot")
@app.post("/chat")
async def chat(chatMessage: chatMessage):
    try:
        chatbot = app.state.chatbot

        status = redis_client.get(chatMessage.thread_id)

        if not status:
            raise HTTPException(
                status_code=404,
                detail="invalid_thread_id"
            )

        # Handle both bytes and str responses from Redis
        if isinstance(status, bytes):
            status = status.decode()
        
        if status != "completed":
            raise HTTPException(
                status_code=409,
                detail=f"thread_not_ready ({status})"
            )

        result = chatbot.invoke(
            {
                "messages": [HumanMessage(content=chatMessage.content)],
                "thread_id": chatMessage.thread_id
            },
            config={
                "configurable": {
                    "thread_id": chatMessage.thread_id
                }
            }
        )

        return {"response": result["messages"][-1].content}

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is

    except Exception as e:
        # Log the full error for debugging
        import traceback
        print("ERROR in /chat endpoint:")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"chat_error: {str(e)}"
        )

@app.get("/threads")
async def get_threads():
    checkpointer = app.state.checkpointer
    threads = retrieve_all_threads(checkpointer)
    return {"threads": threads}

@app.get("/load_chat/{thread_id}")
async def load_chat(thread_id: str):
    chatbot = app.state.chatbot
    messages = loadConv(chatbot, thread_id)
    return {"messages": [msg.dict() for msg in messages]}

@app.post("/process_media")
async def process_media(process_media: processMedia,background_tasks: BackgroundTasks):
    redis_client.set(process_media.thread_id, "queued")
    background_tasks.add_task(main,
                            process_media.path,
                            process_media.media,
                            process_media.thread_id
                            )
    return  {"status": "Processing started"}

@app.get("/ingestion_status/{thread_id}")
def ingestion_status(thread_id: str):
    try:
        status = redis_client.get(thread_id)
        if status is None:
            return {"status": "invalid_thread_id"}
        return {"status": status or "not_found"}
    except Exception as e:
        return {
            "status": "redis_error",
            "detail": str(e)
        }


@app.get("/thread_status/{thread_id}")
def thread_status(thread_id: str):
    try:
        status = redis_client.get(thread_id)

        if not status:
            raise HTTPException(
                status_code=404,
                detail="invalid_thread_id"
            )

        # Handle both bytes and str responses
        if isinstance(status, bytes):
            status = status.decode()

        return {
            "status": status
        }

    except HTTPException:
        raise  # re-raise cleanly

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"redis_error: {str(e)}"
        )