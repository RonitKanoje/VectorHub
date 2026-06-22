from fastapi import APIRouter, Depends, HTTPException, Header
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from threadcore.api.dependencies import ensure_thread_access, get_chatbot, get_current_user
from threadcore.api.schemas import ChatMessageRequest, ChatNameRequest
from threadcore.services.rag.thread_service import (
    save_or_update_thread,
    get_user_thread,
)
from threadcore.infrastructure.db.session import get_db
from threadcore.services.chat.graph import load_conversation
from threadcore.services.chat.naming import title_from_message


router = APIRouter(tags=["chat"])


def _resolve_user(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> str:
    """Get current user ID from header"""
    return get_current_user(x_user_id=x_user_id) ## it will return the current user 


from fastapi.responses import StreamingResponse
import json

@router.post("/chat")
async def chat(
    chat_message: ChatMessageRequest,
    current_user: str = Depends(_resolve_user),
    chatbot=Depends(get_chatbot),
    db: Session = Depends(get_db),
):
    thread = get_user_thread(db, chat_message.thread_id, current_user)
    if thread is None:
        save_or_update_thread(db, chat_message.thread_id, "New Chat", current_user)

    config = {
        "configurable": {
            "thread_id": chat_message.thread_id,
            "user_id": current_user,
        }
    }

    async def event_generator():
        if getattr(chat_message, "is_tool_approval", False):
            if chat_message.content.lower() == "yes":
                stream = chatbot.astream_events(None, config=config, version="v2")
            else:
                from langchain_core.messages import ToolMessage
                state = await chatbot.aget_state(config)
                if state.values and "messages" in state.values:
                    last_message = state.values["messages"][-1]
                    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                        tool_call = last_message.tool_calls[0]
                        tool_msg = ToolMessage(
                            tool_call_id=tool_call["id"],
                            content="User denied permission to use this tool.",
                            name=tool_call["name"]
                        )
                        await chatbot.aupdate_state(config, {"messages": [tool_msg]}, as_node="tools")
                stream = chatbot.astream_events(None, config=config, version="v2")
        else:
            stream = chatbot.astream_events(
                {
                    "messages": [HumanMessage(chat_message.content)],
                    "user_message": chat_message.content,
                },
                config=config,
                version="v2",
            )

        async for event in stream:
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk and isinstance(chunk, str):
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

        state = await chatbot.aget_state(config)
        if state.next and "tools" in state.next:
            if state.values and "messages" in state.values:
                last_msg = state.values["messages"][-1]
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    tool_name = last_msg.tool_calls[0]['name']
                    yield f"data: {json.dumps({'type': 'approval', 'tool': tool_name})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/loadConv/{thread_id}")
async def load_conv(
    thread_id: str,
    current_user: str = Depends(_resolve_user),
    chatbot=Depends(get_chatbot),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, thread_id, current_user)
    messages = await load_conversation(chatbot, thread_id)
    return {"messages": messages} ### you will get messages in key value pair AI : "", Human : ""


@router.post("/nameChat")
async def name_chat(
    payload: ChatNameRequest, #message and thread_id
    current_user: str = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, payload.thread_id, current_user)

    try:
        title = title_from_message(HumanMessage(content=payload.message))
        save_or_update_thread(db, payload.thread_id, title, current_user)
        return {"title": title}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="name_chat_failed") from exc
