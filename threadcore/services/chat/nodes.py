"""Node functions for the conversation graph."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langsmith import traceable

from threadcore.services.chat.llm_config import (
    CONFIDENCE_THRESHOLD,
    get_tool_ready_llm,
    personal_memory_llm,
    route_llm,
    structured_llm,
)
from threadcore.services.chat.prompts import (
    personal_memory_prompt,
    prompt,
    prompt1,
    simple_chat_prompt,
)
from threadcore.services.chat.schemas import ChatState
from threadcore.services.chat.tools_config import tools
from threadcore.services.ingestion.pipeline import (
    long_term_retrieve_answer,
    long_term_store_user_facts,
    retrieve_answer,
)
from threadcore.services.chat.llm_config import llm


# Tool-ready LLM
tool_ready_llm = get_tool_ready_llm(tools)

@traceable
def chat_node(state: ChatState):
    print("\n" + "=" * 50)
    print("CHAT NODE EXECUTED")
    print("State keys:", list(state.keys()))
    print("Context count:", len(state.get("context", [])))
    print("Personal context count:", len(state.get("personal_context", [])))
    print("=" * 50)

    query = state["user_message"]
    context = state.get("context", [])
    meta = state.get("meta", [])
    personal_context = state.get("personal_context", [])

    context_text = "\n\n".join(context) if context else "No relevant context found."
    personal_context_text = (
        "\n\n".join(personal_context)
        if personal_context
        else "No relevant personal memory found."
    )

    meta_text = (
        "\n".join(
            f"- Mentioned at {item['start']}s (duration {item['duration']}s)"
            for item in meta
        )
        if meta
        else "No timing metadata available."
    )

    print("\nCONTEXT PREVIEW:")
    print(context_text[:1000])
    print("\nEND CONTEXT PREVIEW\n")

    messages = state.get("messages", []).copy()

    if not messages:
        messages.append(
            SystemMessage(content=prompt1.template)
        )

    messages.append(
        HumanMessage(
            content=f"""Context (use only if relevant):
{context_text}

Personal memory (use only for questions about the user):
{personal_context_text}

Timing metadata (ONLY for 'when/where' questions):
{meta_text}

User question:
{query}"""
        )
    )

    print("\nFINAL PROMPT SENT TO LLM:")
    print(messages[-1].content[:2000])
    print("\nEND PROMPT\n")

    result = structured_llm.invoke(messages)

    print("\nLLM RESPONSE:")
    print(result)
    print("CONFIDENCE:", result.confidence)
    print("=" * 50)

    if result.confidence < CONFIDENCE_THRESHOLD:
        print("LOW CONFIDENCE -> TOOL PATH")

        tool_response = tool_ready_llm.invoke(messages)

        return {
            "messages": [tool_response],
            "confidence": result.confidence,
        }

    print("HIGH CONFIDENCE -> DIRECT ANSWER")

    return {
        "messages": [AIMessage(content=result.answer)],
        "confidence": result.confidence,
    }   
@traceable(name="RAG Tool")
def rag_node(state: ChatState, config) -> dict:
    print("rag_node")
    """Retrieve context from ingestion pipeline."""
    thread_id = config["configurable"]["thread_id"]
    user_id = config["configurable"]["user_id"]
    query = state["user_message"]

    result = retrieve_answer(query, user_id=user_id, thread_id=thread_id)
    contexts = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {"context": contexts, "meta": metadata}


@traceable(name="Personal Memory")
def personal_memory_node(state: ChatState, config) -> dict:
    """Store and retrieve durable personal facts for the current user."""
    user_id = config["configurable"]["user_id"]
    query = state["user_message"]

    try:
        decision = personal_memory_llm.invoke(
            [
                SystemMessage(content=personal_memory_prompt.template),
                HumanMessage(content=query),
            ]
        )
        facts = [fact.strip() for fact in decision.facts if fact.strip()]
        should_retrieve = decision.should_retrieve
        should_store = decision.should_store and bool(facts)
    except Exception:
        facts = []
        should_retrieve = _looks_like_personal_query(query)
        should_store = False

    if should_store:
        long_term_store_user_facts(facts, user_id=user_id)

    personal_context = []
    if should_retrieve or should_store:
        result = long_term_retrieve_answer(query, user_id=user_id)
        personal_context = [doc.page_content for doc in result]

    return {
        "personal_context": personal_context,
        "stored_personal_facts": facts if should_store else [],
    }

@traceable
def _looks_like_personal_query(query: str) -> bool:
    """Fallback heuristic when structured personal-memory routing fails."""
    lowered = query.lower()
    personal_markers = (
        "my ",
        "me ",
        "i am",
        "i'm",
        "i like",
        "i prefer",
        "remember",
        "what is my",
        "what's my",
        "who am i",
    )
    return any(marker in lowered for marker in personal_markers)

@traceable
def intent_node(state: ChatState):
    print("intent_node")
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

@traceable
def simple_chat_node(state: ChatState): 
    print("chat_node")  
    """Handle simple chat without context."""
    query = state["user_message"]
    personal_context = state.get("personal_context", [])
    personal_context_text = (
        "\n\n".join(personal_context)
        if personal_context
        else "No relevant personal memory found."
    )

    messages = state.get("messages", []).copy()
    if not messages:
        messages.append(SystemMessage(content=simple_chat_prompt.template))

    messages.append(
        HumanMessage(
            content=f"""Personal memory (use only for questions about the user):
{personal_context_text}

User message:
{query}"""
        )
    )
    response = llm.invoke(messages)
    return {"messages": [response]}
