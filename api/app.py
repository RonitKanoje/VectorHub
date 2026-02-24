from fastapi import FastAPI, HTTPException, BackgroundTasks
from api.schemas import UserCreate, UserLogin, chatName, processMedia,chatName
from backend.hashing import hash_password, verify_password
from database.postgres.checkpointer import get_checkpointer
from langchain_core.messages import HumanMessage
import json
from backend.main import main
from chatbot.chatbot import build_chatbot
from api.schemas import processMedia,chatMessage
from backend.status import redis_client
from database.postgres.users import create_user, get_user_by_username
from database.postgres.users import create_user
from database.qdrant.vectorStore import create_vector_store
from fastapi import HTTPException
from langsmith import traceable
from chatbot.chatbot import loadConv
from chatbot.nameChat import title_from_message 
from database.postgres.thread import get_db_connection, create_thread_with_title
from psycopg.errors import UniqueViolation

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
async def register(user: UserCreate):
    try:
        password_hash = hash_password(user.password)

        result = create_user(user.username, password_hash)

        if not result:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        return {
            "status": "success",
            "message": "User created successfully"
        }

    except UniqueViolation:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    except Exception as e:
        print("REGISTER ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="User registration failed"
        )

# @app.post("/get_password_hash")
# async def get_password_hash(user: UserCreate):
#     password = user.password
#     return {"password_hash": password}

@app.post("/login")
async def login(user: UserLogin):
    try:
        db_user = get_user_by_username(user.username)

        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        user_id, username, stored_hash = db_user

        if not verify_password(user.password, stored_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        return {
            "status": "success",
            "message": "Login successful",
            "user_id": user_id,
            "username": username
        }

    except HTTPException:
        raise

    except Exception as e:
        print("LOGIN ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )