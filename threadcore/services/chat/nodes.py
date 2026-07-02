"""Node functions for the conversation graph."""

import traceback
from unittest import result

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
from threadcore.services.ingestion.pipeline import retrieve_answer
from threadcore.services.chat.llm_config import llm
from threadcore.services.rag.memory_service import (
    store_user_memories,
     retrieve_user_memories
)


# Tool-ready LLM
tool_ready_llm = get_tool_ready_llm(tools)

@traceable
def chat_node(state: ChatState):
    query = state["user_message"]

    context = state.get("context", [])
    meta = state.get("meta", [])
    personal_context = state.get("personal_context", [])

    context_text = (
        "\n\n".join(context)
        if context
        else "No relevant RAG context available."
    )

    personal_memory_text = (
        "\n".join(f"- {m}" for m in personal_context)
        if personal_context
        else "No personal memory available."
    )

    metadata_text = (
        "\n".join(
            [
                (
                    f"- {item.get('type')}: start={item['start']}, duration={item['duration']}"
                    if "start" in item and "duration" in item
                    else (
                        f"- {item.get('type')}: {item['location']}"
                        if "location" in item
                        else f"- {item.get('type')}"
                    )
                )
                for item in meta
            ]
        )
        if meta
        else "No timing metadata."
    )

    # Previous conversation (without duplicating the latest user message)
    history = state.get("messages", []).copy()

    # Remove the last HumanMessage because we will send it again
    if history and isinstance(history[-1], HumanMessage):
        history = history[:-1]

    messages = [

        # Always include the system prompt
        SystemMessage(
            content="""
You are VectorHub.

You have access to THREE information sources.

1. PERSONAL MEMORY
- These are persistent facts about the user.
- They are true unless contradicted.
- Use them whenever the user asks about themselves.
- Examples:
  - What is my name?
  - Where do I study?
  - What are my goals?
  - What projects am I building?

2. RAG CONTEXT
- This comes from uploaded documents.
- Use it ONLY for questions about uploaded content.

3. GENERAL KNOWLEDGE
- If neither Personal Memory nor RAG contains the answer,
  answer from your own knowledge.

Priority:

Personal Memory
    ↓
RAG Context
    ↓
General Knowledge

Never ignore Personal Memory if it answers the user's question.
"""
        ),

        SystemMessage(
            content=f"""
=========================
PERSONAL MEMORY
=========================

{personal_memory_text}

=========================
RAG CONTEXT
=========================

{context_text}

=========================
TIMING METADATA
=========================

{metadata_text}
"""
        ),

        *history,

        HumanMessage(content=query),
    ]

    print("=" * 80)
    print("FINAL PROMPT")
    print("=" * 80)

    for m in messages:
        print(type(m).__name__)
        print(m.content)
        print("-" * 80)

    result = structured_llm.invoke(messages)

    print("=" * 80)
    print("CHAT NODE RESULT")
    print(result)
    print(type(result))
    print("=" * 80)

    if result.confidence < CONFIDENCE_THRESHOLD:

        tool_response = tool_ready_llm.invoke(messages)

        return {
            "messages": [tool_response],
            "confidence": result.confidence,
        }

    return {
        "messages": [AIMessage(content=result.answer)],
        "confidence": result.confidence,
    }


@traceable(name="RAG Tool")
def rag_node(state: ChatState, config) -> dict:

    
    thread_id = config["configurable"]["thread_id"]
    user_id = config["configurable"]["user_id"]
    query = state["user_message"]

    result = retrieve_answer(query, user_id=user_id, thread_id=thread_id)
    
    
    contexts = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {"context": contexts, "meta": metadata}


@traceable(name="Personal Memory")
def personal_memory_node(state: ChatState, config):
    user_id = config["configurable"]["user_id"]
    query = state["user_message"]

    print("====================================================")
    print("ENTERED personal_memory_node")
    print("====================================================")
    print("User message:", query)
    print("Resolved user_id:", user_id)

    try:
        print("Calling personal_memory_llm.invoke()")
        decision = personal_memory_llm.invoke(
            [
                SystemMessage(content=personal_memory_prompt.template),
                HumanMessage(content=query),
            ]
        )
        print("LLM response:", decision)
        print("LLM response type:", type(decision))
        if hasattr(decision, "model_dump"):
            print("Structured response dict:", decision.model_dump())
        else:
            print("Structured response repr:", repr(decision))

        facts = [fact.strip() for fact in getattr(decision, "facts", []) if fact and str(fact).strip()]
        decision_should_store = bool(getattr(decision, "should_store", False))
        should_store = decision_should_store and bool(facts)

        print("Parsed PersonalMemoryDecision:")
        print("should_store from Gemini:", decision_should_store)
        print("facts:", facts)
        print("should_retrieve:", getattr(decision, "should_retrieve", None))
        print("Effective should_store:", should_store)
        if not decision_should_store:
            print("EARLY RETURN CANDIDATE: Gemini returned should_store=False")
        if not facts:
            print("EARLY RETURN CANDIDATE: Gemini returned no facts")
        print("facts:", facts)

    except Exception:
        print("Exception from personal_memory_llm.invoke()")
        traceback.print_exc()
        raise

    if should_store:
        print("Calling store_user_memories()")
        print("user_id:", user_id)
        print("facts:", facts)
        store_user_memories(user_id=user_id, memories=facts)
        print("EXIT store_user_memories call in personal_memory_node")
    else:
        print("EARLY RETURN: store_user_memories() not called")
        print("Skipping store_user_memories() because should_store=False or facts=[]")

    memories = retrieve_user_memories(user_id=user_id)
    personal_context = [m.memory_text for m in memories]

    print("Retrieved personal_context:", personal_context)
    print("EXIT personal_memory_node")

    return {
        "personal_context": personal_context,
        "stored_personal_facts": facts if should_store else [],
    }


def _looks_like_personal_query(query: str) -> bool:
    lowered = query.lower()
    personal_markers = ("my ", "me ", "i am", "i'm", "i like", "i prefer",
                        "remember", "what is my", "what's my", "who am i")
    return any(marker in lowered for marker in personal_markers)


@traceable(name="INTENT_NODE_TRACE")
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
    """Handle simple chat without context."""
    query = state["user_message"]
    personal_context = state.get("personal_context", [])  # ← add this

    personal_context_text = (
        "\n".join(f"- {m}" for m in personal_context)
        if personal_context
        else "No personal memory found."
    )

    messages = state.get("messages", []).copy()
    if not messages:
        messages.append(SystemMessage(content=simple_chat_prompt.template))

    messages.append(
        HumanMessage(
            content=f"""Known facts about this user:
{personal_context_text}

User message:
{query}"""
        )
    )
    response = llm.invoke(messages)
    return {"messages": [response]}
