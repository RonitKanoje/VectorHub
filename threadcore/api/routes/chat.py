from fastapi import APIRouter, Depends, HTTPException, Header
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from threadcore.api.dependencies import ensure_thread_access, get_chatbot, get_current_user
from threadcore.api.schemas import ChatMessageRequest, ChatNameRequest
from threadcore.infrastructure.cache.redis_client import redis_client
from threadcore.infrastructure.db.models import UserDB
from threadcore.infrastructure.db.repositories import create_or_update_thread
from threadcore.infrastructure.db.session import get_db
from threadcore.services.chat.graph import load_conversation
from threadcore.services.chat.naming import title_from_message


router = APIRouter(tags=["chat"])


def _resolve_user(x_user_id: str = Header(..., alias="X-User-Id"), db: Session = Depends(get_db)):
    return get_current_user(x_user_id=x_user_id, db=db)


@router.post("/chat")
async def chat(
    chat_message: ChatMessageRequest,
    current_user: UserDB = Depends(_resolve_user),
    chatbot=Depends(get_chatbot),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, chat_message.thread_id, current_user.id)

    status = redis_client.get(chat_message.thread_id)
    if not status:
        raise HTTPException(status_code=404, detail="invalid_thread_id")
    if status != "completed":
        raise HTTPException(status_code=409, detail=f"thread_not_ready ({status})")

    result = chatbot.invoke(
        {
            "messages": [HumanMessage(chat_message.content)],
            "user_message": chat_message.content,
        },
        config={
            "configurable": {
                "thread_id": chat_message.thread_id,
                "user_id": current_user.id,
            }
        },
    )

    return {"response": result["messages"][-1].content}


@router.get("/loadConv/{thread_id}")
async def load_conv(
    thread_id: str,
    current_user: UserDB = Depends(_resolve_user),
    chatbot=Depends(get_chatbot),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, thread_id, current_user.id)
    return {"messages": load_conversation(chatbot, thread_id)}


@router.post("/nameChat")
async def name_chat(
    payload: ChatNameRequest,
    current_user: UserDB = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, payload.thread_id, current_user.id)

    try:
        title = title_from_message(HumanMessage(content=payload.message))
        create_or_update_thread(db, payload.thread_id, title, current_user.id)
        return {"title": title}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="name_chat_failed") from exc
