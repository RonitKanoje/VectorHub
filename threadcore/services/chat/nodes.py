"""Node functions for the conversation graph."""

import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langsmith import traceable

from threadcore.services.chat.llm_config import (
    llm,
    personal_memory_llm,
    route_llm,
)
from threadcore.services.chat.prompts import (
    personal_memory_prompt,
    prompt,
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

logger = logging.getLogger(__name__)

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

    logger.debug(
        "Final prompt:\n%s",
        "\n\n".join(f"{type(m).__name__}\n{m.content}" for m in base_messages),
    )

    # Second pass: ToolNode has already executed.
    # Just generate the final answer.
    if is_after_tool:
        structured_answer = structured_llm.invoke(base_messages)

        return {
            "messages": [AIMessage(content=structured_answer.answer)],
            "can_answer_without_tools": True,
        }

    # First pass: generate answer + tool decision
    structured_answer = structured_llm.invoke(base_messages)

    if not structured_answer.can_answer_without_tools:
        return {
            "can_answer_without_tools": False,
        }

    return {
        "messages": [AIMessage(content=structured_answer.answer)],
        "can_answer_without_tools": True,
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
    logger.debug("Tool selection output: %s", getattr(ai_message, "tool_calls", None))

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
    if contexts:
        logger.info("RAG retrieval completed: %s documents", len(contexts))
        logger.debug("Retrieved RAG context count: %s", len(contexts))
    else:
        logger.warning("No RAG documents found")

    return {"context": contexts, "meta": metadata}


@traceable(name="Personal Memory")
def personal_memory_node(state: ChatState, config):
    user_id = config["configurable"]["user_id"]
    query = state["user_message"]

    try:
        logger.debug("Invoking personal memory decision LLM")
        decision = personal_memory_llm.invoke(
            build_llm_context(
                messages=[],
                system_messages=SystemMessage(content=personal_memory_prompt.template),
                current_user_message=query,
            )
        )

        if hasattr(decision, "model_dump"):
            logger.debug("Personal memory structured response: %s", decision.model_dump())
        else:
            logger.debug("Personal memory structured response: %r", decision)

        facts = [fact.strip() for fact in getattr(decision, "facts", []) if fact and str(fact).strip()]
        decision_should_store = bool(getattr(decision, "should_store", False))
        should_store = decision_should_store and bool(facts)

        logger.debug(
            "Personal memory decision parsed: should_store=%s facts=%s should_retrieve=%s effective_should_store=%s",
            decision_should_store,
            facts,
            getattr(decision, "should_retrieve", None),
            should_store,
        )
        if not decision_should_store:
            logger.debug("Personal memory LLM returned should_store=False")
        if not facts:
            logger.debug("Personal memory LLM returned no facts")

    except Exception:
        logger.exception("Personal memory LLM invocation failed")
        raise

    if should_store:
        logger.debug("Storing personal memories for user_id=%s facts=%s", user_id, facts)
        store_user_memories(user_id=user_id, memories=facts)
        logger.info("Memory stored successfully")
    else:
        logger.debug("Skipping memory storage because should_store=False or facts=[]")

    memories = retrieve_user_memories(user_id=user_id)
    personal_context = [m.memory_text for m in memories]

    if personal_context:
        logger.debug("Retrieved personal memories: %s", personal_context)
    else:
        logger.warning("No personal memories retrieved")

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
    """Route query to RAG or general chat."""
    messages = build_llm_context(
        messages=[],
        system_messages=SystemMessage(content=prompt.template),
        current_user_message=state["user_message"],
    )

    try:
        result = route_llm.invoke(messages)
        route = result.decision
        logger.info("Intent classification completed: %s", route)
    except Exception:
        logger.exception("Intent classification failed; falling back to chat")
        route = "chat"

    return {"route": route}


@traceable
def simple_chat_node(state: ChatState):
    """Handle simple chat without context."""
    return {}
