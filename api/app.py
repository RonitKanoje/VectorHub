from fastapi import FastAPI
from database.postgres.checkpointer import get_checkpointer
from langchain_core.messages import HumanMessage
from chatbot.chatbot import retrieve_all_threads, loadConv
import json
from backend.main import main
from chatbot.chatbot import build_chatbot

app = FastAPI()

@app.get("/")
async def read_root():
    return {"status": "API is running"}

@app.on_event("startup")
def startup():
    app.state.checkpointer = get_checkpointer()
    app.state.chatbot = build_chatbot(app.state.checkpointer)

@app.post("/chat")
async def chat(payload: dict):
    chatbot = app.state.chatbot

    result = chatbot.invoke(
        {"messages": [HumanMessage(content=payload["message"])]},
        config={
            "configurable": {
                "thread_id": payload["thread_id"]
            }
        }
    )

    return {"response": result["messages"][-1].content}


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

##main(video_id,"youtube",st.session_state.thread_id)
@app.post("/process_media")
async def process_media(payload: dict):
    path = payload["path"]
    media = payload["media"]
    thread_id = payload["thread_id"]
    await main(path, media, thread_id)
    return {"status": "Processing started"}