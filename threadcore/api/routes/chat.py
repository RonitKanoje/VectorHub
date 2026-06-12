from fastapi import APIRouter, Depends, HTTPException, Header
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from threadcore.api.dependencies import ensure_thread_access, get_chatbot, get_current_user
from threadcore.api.schemas import ChatMessageRequest, ChatNameRequest
from threadcore.infrastructure.db.repositories import (
    create_or_update_thread,
    get_thread_for_user,
)
from threadcore.infrastructure.db.session import get_db
from threadcore.services.chat.graph import load_conversation
from threadcore.services.chat.naming import title_from_message


router = APIRouter(tags=["chat"])


def _resolve_user(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> str:
    """Get current user ID from header"""
    return get_current_user(x_user_id=x_user_id) ## it will return the current user 


@router.post("/chat")
async def chat(
    chat_message: ChatMessageRequest, ## schema
    current_user: str = Depends(_resolve_user), ##get current user
    chatbot=Depends(get_chatbot),
    db: Session = Depends(get_db), ## db
):
    thread = get_thread_for_user(db, chat_message.thread_id, current_user)
    if thread is None:
        create_or_update_thread(db, chat_message.thread_id, "New Chat", current_user)

    result = chatbot.invoke(
        {
            "messages": [HumanMessage(chat_message.content)],
            "user_message": chat_message.content,
        },
        config={
            "configurable": {
                "thread_id": chat_message.thread_id,
                "user_id": current_user,
            }
        },
    )

    return {"response": result["messages"][-1].content}


@router.get("/loadConv/{thread_id}")
async def load_conv(
    thread_id: str,
    current_user: str = Depends(_resolve_user),
    chatbot=Depends(get_chatbot),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, thread_id, current_user)
    return {"messages": load_conversation(chatbot, thread_id)} ### you will get messages in key value pair AI : "", Human : ""


@router.post("/nameChat")
async def name_chat(
    payload: ChatNameRequest, #message and thread_id
    current_user: str = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, payload.thread_id, current_user)

    try:
        title = title_from_message(HumanMessage(content=payload.message))
        create_or_update_thread(db, payload.thread_id, title, current_user)
        return {"title": title}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="name_chat_failed") from exc
