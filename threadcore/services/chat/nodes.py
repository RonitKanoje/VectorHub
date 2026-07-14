"""Node functions for the conversation graph."""

import traceback

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langsmith import traceable

from threadcore.services.chat.llm_config import (
    CONFIDENCE_THRESHOLD,
    llm,
    personal_memory_llm,
    route_llm,
)
from threadcore.services.chat.prompts import (
    personal_memory_prompt,
    prompt,
    simple_chat_prompt,
    vectorhub_system_prompt,
)
from threadcore.services.chat.schemas import ChatState, StructuredAnswer
from threadcore.services.chat.tools_config import tools
from threadcore.services.context_builder import build_llm_context
from threadcore.services.ingestion.pipeline import retrieve_answer
from threadcore.services.rag.memory_service import (
    store_user_memories,
    retrieve_user_memories,
)

tool_llm = llm.bind_tools(tools)

structured_llm = llm.with_structured_output(StructuredAnswer)

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
        )
        if meta
        else "No timing metadata."
    )

    system_messages = [
        SystemMessage(
            content=vectorhub_system_prompt.format(
                personal_memory_text=personal_memory_text,
                context_text=context_text,
                metadata_text=metadata_text,
            )
        )
    ]

    history = state.get("messages", [])
    is_after_tool = bool(history and isinstance(history[-1], ToolMessage))

    base_messages = build_llm_context(
        messages=history,
        system_messages=system_messages,
        current_user_message=None if is_after_tool else query,
        conversation_summary=state.get("conversation_summary", ""),
        important_facts=state.get("important_facts", []),
    )

    print("=" * 80)
    print("FINAL PROMPT")
    print("=" * 80)
    for m in base_messages:
        print(type(m).__name__)
        print(m.content)
        print("-" * 80)

    # Second pass: ToolNode has already executed.
    # Just generate the final answer.
    if is_after_tool:
        structured_answer = structured_llm.invoke(base_messages)

        return {
            "messages": [AIMessage(content=structured_answer.answer)],
            "confidence": 1.0,  # Prevent re-entering tool routing
        }

    # First pass: generate answer + confidence
    structured_answer = structured_llm.invoke(base_messages)

    return {
        "messages": [AIMessage(content=structured_answer.answer)],
        "confidence": structured_answer.confidence,
    }

@traceable
def tool_node(state: ChatState):
    query = state["user_message"]

    history = state.get("messages", [])

    messages = build_llm_context(
        messages=history,
        current_user_message=query,
        conversation_summary=state.get("conversation_summary", ""),
        important_facts=state.get("important_facts", []),
    )

    ai_message = tool_llm.invoke(messages)

    return {
        "messages": [ai_message],
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

    try:
        print("Calling personal_memory_llm.invoke()")
        decision = personal_memory_llm.invoke(
            build_llm_context(
                messages=[],
                system_messages=SystemMessage(content=personal_memory_prompt.template),
                current_user_message=query,
            )
        )

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
    messages = build_llm_context(
        messages=[],
        system_messages=SystemMessage(content=prompt.template),
        current_user_message=state["user_message"],
    )

    try:
        result = route_llm.invoke(messages)
        route = result.decision
    except Exception:
        route = "chat"

    return {"route": route}


@traceable
def simple_chat_node(state: ChatState):
    """Handle simple chat without context."""
    return {}
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
    response = llm.invoke(
        build_llm_context(
            messages=messages,
            current_user_message=query,
            conversation_summary=state.get("conversation_summary", ""),
            important_facts=state.get("important_facts", []),
        )
    )
    return {"messages": [response]}
