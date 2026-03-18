from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from typing import List
from sqlalchemy.orm import Session

# Schemas
from api.schemas import (
    AccessTokenResponse,
    UserCreate,
    UserResponse,
    chatName,
    processMedia,
    chatMessage
)

# Utils
from utils.hashing import hash_password, verify_password
from utils.jwt_handler import (
    create_access_token,
    get_current_user,
    get_current_active_user
)

# Database
from database.postgres.userdb import (
    UserDB,
    get_user_by_username,
    get_db,
    get_all_users
)
from database.postgres.checkpointer import get_checkpointer
from database.postgres.thread import create_thread_with_title

# Vector DB
from database.qdrant.vectorStore import create_vector_store

# Chatbot
from chatbot.chatbot import build_chatbot, loadConv
from chatbot.nameChat import title_from_message

# Backend
from backend.main import main
from backend.status import redis_client

# Other
from langchain_core.messages import HumanMessage
from langsmith import traceable
from psycopg.errors import UniqueViolation

import json


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
        print("Incoming message:", chatMessage)
        print("Thread ID type:", type(chatMessage.thread_id))
        print("Thread ID value:", chatMessage.thread_id)

        chatbot = app.state.chatbot

        status = redis_client.get(chatMessage.thread_id)
        print("Redis status raw:", status)

        if not status:
            raise HTTPException(404, "invalid_thread_id")

        if isinstance(status, bytes):
            status = status.decode()

        print("Redis status decoded:", status)

        if status != "completed":
            raise HTTPException(409, f"thread_not_ready ({status})")

        result = chatbot.invoke(
            {
                "messages": [HumanMessage(chatMessage.content)],
                "user_message": chatMessage.content,
            },
            config={
                "configurable": {
                    "thread_id": chatMessage.thread_id
                }
            }
        )

        return {"response": result["messages"][-1].content}

    except Exception as e:
        print("CHAT ERROR FULL:", repr(e))
        raise

# @app.get("/threads")
# async def get_threads():
#     checkpointer = app.state.checkpointer
#     threads = retrieve_all_threads(checkpointer)
#     return {"threads": threads}

@app.get("/threads")
async def get_threads():
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT thread_id, title FROM threads")
                threads = [{"thread_id": row[0], "title": row[1]} for row in cur.fetchall()]
            return {"threads": threads}
        finally:
            conn.close()
    except Exception as e:
        print("GET THREADS ERROR:", e)
        raise HTTPException(500, "get_threads_failed")
    

@app.post("/process_media")
async def process_media(process_media: processMedia,background_tasks: BackgroundTasks):
    redis_client.set(process_media.thread_id, "queued")
    background_tasks.add_task(main,
                            process_media.path,
                            process_media.media,
                            process_media.thread_id,
                            process_media.language
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
    
# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}    


@app.get("/loadConv/{thread_id}")
async def load_conversation(thread_id: str):
    chatbot = app.state.chatbot
    messages = loadConv(chatbot, thread_id)
    return {"messages": messages}

@app.post("/nameChat")
async def name_chat(message: chatName):
    try:
        title = title_from_message(HumanMessage(content=message.message))
        create_thread_with_title(message.thread_id, title)
        return {"title": title}
    except Exception as e:
        print("NAME CHAT ERROR:", e)
        raise HTTPException(500, "name_chat_failed")

@app.post("/register")
def register(user: UserCreate,db : Session = Depends(get_db)):
    try:
        existing_user = get_user_by_username(db,user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
##################################
        hashed_password = hash_password(user.password)
        new_user = UserDB(name = user.name,username=user.username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully"}
    except Exception as e:
        print("REGISTRATION ERROR:", e)
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/token",response_model=AccessTokenResponse)
def login_access_token(form_data : OAuth2PasswordRequestForm
 = Depends(), db: Session = Depends(get_db)):
    try:
        user = get_user_by_username(db,form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        access_token = create_access_token(data={"user_id": user.id})
        return AccessTokenResponse(access_token=access_token, token_type="bearer")
    except Exception as e:
        print("LOGIN ERROR:", e)
        raise HTTPException(status_code=500, detail="Login failed")
    
#API Endpoints for CRUD operation

@app.get("/profile")  # no need for user_id in URL
def get_profile(current_user: UserDB = Depends(get_current_active_user)):
    try:
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        return current_user
    except HTTPException:
        raise  # re-raise 404 cleanly
    except Exception as e:
        print("PROFILE ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")
    

@app.get("/users",response_model=List[UserResponse])
def get_users():
    try:
        users = get_all_users()
        return users
    except Exception as e:
        print("USERS ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve users")
