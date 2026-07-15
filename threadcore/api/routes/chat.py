import json
import logging
import os
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langchain_core.messages import ToolMessage
from sqlalchemy.orm import Session
from threadcore.api.dependencies import ensure_thread_access, get_chatbot, get_current_user
from threadcore.api.schemas import ChatMessageRequest, ChatNameRequest, ThreadNameFromUploadRequest
from threadcore.services.rag.thread_service import (
    save_or_update_thread,
    get_user_thread,
)
from threadcore.infrastructure.db.session import get_db
from threadcore.services.chat.graph import load_conversation
from threadcore.services.chat.llm_config import llm as context_llm
from threadcore.services.chat.naming import title_from_message
from threadcore.services.context_builder import schedule_context_cache_refresh

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)


def _resolve_user(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> str:
    """Get current user ID from header"""
    return get_current_user(x_user_id=x_user_id)


@router.post("/chat")
async def chat(
    chat_message: ChatMessageRequest,
    current_user: str = Depends(_resolve_user),
    chatbot=Depends(get_chatbot),
    db: Session = Depends(get_db),
):
    logger.info("Chat request received")
    thread = get_user_thread(db, chat_message.thread_id, current_user)

    if thread is None:
        save_or_update_thread(
            db,
            chat_message.thread_id,
            "New Chat",
            current_user,
            mode="chat"
        )

    config = {
        "configurable": {
            "thread_id": chat_message.thread_id,
            "user_id": current_user,
        }
    }

    async def event_generator():
        logger.warning(
        "TRACING_CHECK tracing=%s api_key_prefix=%s project=%s",
        os.environ.get("LANGSMITH_TRACING") or os.environ.get("LANGCHAIN_TRACING_V2"),
        (os.environ.get("LANGSMITH_API_KEY") or "")[:8],
        os.environ.get("LANGSMITH_PROJECT"),
    )
        try:
            
            # If the message is a tool approval, handle it accordingly
            if getattr(chat_message, "is_tool_approval", False):
                if chat_message.content.lower() == "yes":
                    logger.info("Tool execution approved; resuming graph")

                    stream = chatbot.astream_events(
                        None,
                        config=config,
                        version="v2",
                    )
                else:  ## user denied tool usage 
                    logger.info("Tool execution rejected; resuming graph with denial ToolMessage")
                    state = await chatbot.aget_state(config)

                    if state.values and "messages" in state.values:
                        last_message = state.values["messages"][-1]

                        if (
                            hasattr(last_message, "tool_calls")
                            and last_message.tool_calls
                        ):
                            tool_call = last_message.tool_calls[0]

                            tool_msg = ToolMessage(
                                tool_call_id=tool_call["id"],
                                content="User denied permission to use this tool.",
                                name=tool_call["name"],
                            )

                            await chatbot.aupdate_state(
                                config,
                                {"messages": [tool_msg]},
                                as_node="tools",
                            )

                    stream = chatbot.astream_events( ## returns an asynchronous event generator.
                        None,
                        config=config,
                        version="v2",
                    )

            else:
                stream = chatbot.astream_events(
                    {
                        "messages": [
                            HumanMessage(chat_message.content)
                        ],
                        "user_message": chat_message.content,
                    },
                    config=config,
                    version="v2",
                )

            async for event in stream:
                try:
                    event_type = event.get("event")
                    node_name = event.get("name")
                
                    langgraph_node = event.get("metadata", {}).get("langgraph_node", "")

                    data = event.get("data")

                    if event_type == "on_chat_model_stream":
                        continue

                    if event_type == "on_chain_stream" and node_name == "chat_node":
                        continue

                    if event_type == "on_chain_end" and node_name == "chat_node":
                        output = event.get("data", {}).get("output", {})
                        if isinstance(output, dict) and "messages" in output:
                            msgs = output["messages"]
                            if msgs:
                                last_msg = msgs[-1]
                                if (
                                    hasattr(last_msg, "content")
                                    and isinstance(last_msg.content, str)
                                    and last_msg.content
                                    and not getattr(last_msg, "tool_calls", None)
                                ):
                                    yield (
                                        f"data: "
                                        f"{json.dumps({'type':'chunk','content':last_msg.content})}\n\n"
                                    )

                except Exception as e:
                    logger.exception("Error while processing chat stream event")
                    raise


            state = await chatbot.aget_state(config)

            if state.next and "tools" in state.next:

                if state.values and "messages" in state.values:
                    last_msg = state.values["messages"][-1]

                    if (
                        hasattr(last_msg, "tool_calls")
                        and last_msg.tool_calls
                    ):
                        tool_name = last_msg.tool_calls[0]["name"]
                        logger.debug("Tool approval required for tool: %s", tool_name)

                        yield (
                            f"data: "
                            f"{json.dumps({'type':'approval','tool':tool_name})}\n\n"
                        )
            else:
                schedule_context_cache_refresh(
                    app=chatbot,
                    config=config,
                    llm=context_llm,
                    as_node="chat_node",
                )
                logger.info("Request completed successfully")

            yield "data: [DONE]\n\n"

        except Exception as e:      
            logger.exception("Chat request failed")

            yield (
                f"data: "
                f"{json.dumps({'type':'error','content':str(e)})}\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


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
        save_or_update_thread(db, payload.thread_id, title, current_user, mode="chat")
        return {"title": title}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="name_chat_failed") from exc


@router.post("/nameThreadFromUpload")
async def name_thread_from_upload(
    payload: ThreadNameFromUploadRequest,
    current_user: str = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    try:
        thread = get_user_thread(db, payload.thread_id, current_user)
        
        # If thread already exists and is not named "New Chat", keep existing name
        if thread and thread.title and thread.title != "New Chat":
            return {"title": thread.title}

        
        # Clean up the filename: remove extension, replace hyphens/underscores, title case
        name_without_ext = os.path.splitext(payload.filename)[0]
        clean_name = name_without_ext.replace("_", " ").replace("-", " ").strip().title()
        
        title = clean_name if clean_name else f"{payload.media.capitalize()} Upload"

        save_or_update_thread(db, payload.thread_id, title, current_user, mode=thread.mode if thread else "chat")
        return {"title": title}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="name_thread_from_upload_failed") from exc
