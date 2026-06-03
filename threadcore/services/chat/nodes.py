"""Node functions for the conversation graph."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langsmith import traceable

from threadcore.services.chat.llm_config import (
    CONFIDENCE_THRESHOLD,
    get_tool_ready_llm,
    route_llm,
    structured_llm,
)
from threadcore.services.chat.prompts import prompt, prompt1, simple_chat_prompt
from threadcore.services.chat.schemas import ChatState
from threadcore.services.chat.tools_config import tools
from threadcore.services.ingestion.pipeline import retrieve_answer
from threadcore.services.chat.llm_config import llm


# Tool-ready LLM
tool_ready_llm = get_tool_ready_llm(tools)


def chat_node(state: ChatState):
    """Process user query with context and return response."""
    query = state["user_message"]
    context = state.get("context", [])
    meta = state.get("meta", [])

    context_text = "\n\n".join(context) if context else "No relevant context found."
    meta_text = (
        "\n".join(f"- Mentioned at {item['start']}s (duration {item['duration']}s)" for item in meta)
        if meta
        else "No timing metadata available."
    )

    messages = state.get("messages", []).copy()
    if not messages:
        messages.append(SystemMessage(content=prompt1.template))

    messages.append(
        HumanMessage(
            content=f"""Context (use only if relevant):
{context_text}

Timing metadata (ONLY for 'when/where' questions):
{meta_text}

User question:
{query}"""
        )
    )

    result = structured_llm.invoke(messages)
    if result.confidence < CONFIDENCE_THRESHOLD:
        tool_response = tool_ready_llm.invoke(messages)
        return {"messages": [tool_response], "confidence": result.confidence}

    return {"messages": [AIMessage(content=result.answer)], "confidence": result.confidence}


@traceable(name="RAG Tool")
def rag_node(state: ChatState, config) -> dict:
    """Retrieve context from ingestion pipeline."""
    thread_id = config["configurable"]["thread_id"]
    user_id = config["configurable"]["user_id"]
    query = state["user_message"]

    result = retrieve_answer(query, user_id=user_id, thread_id=thread_id)
    contexts = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {"context": contexts, "meta": metadata}


def intent_node(state: ChatState):
    """Route query to RAG or general chat."""
    messages = [
        SystemMessage(content=prompt.template),
        HumanMessage(content=state["user_message"]),
    ]

    try:
        result = route_llm.invoke(messages)
        route = result.decision
    except Exception:
        route = "chat"

    return {"route": route}


def simple_chat_node(state: ChatState):
    """Handle simple chat without context."""
    messages = state.get("messages", []).copy()
    if not messages:
        messages.append(SystemMessage(content=simple_chat_prompt.template))

    messages.append(HumanMessage(content=state["user_message"]))
    response = llm.invoke(messages)
    return {"messages": [response]}
