from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import BaseModel, Field

from ai.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ContextBuilderConfig:
    summary_threshold: int = settings.context_summary_threshold
    recent_message_limit: int = settings.context_recent_message_limit
    summary_min_new_messages: int = settings.context_summary_min_new_messages
    summary_max_transcript_chars: int = settings.context_summary_max_transcript_chars
    important_fact_limit: int = settings.context_important_fact_limit


class ContextCacheUpdate(BaseModel):
    conversation_summary: str = Field(
        description="A specific, durable summary of goals, completed tasks, decisions, assumptions, conclusions, and unresolved work."
    )
    important_facts: list[str] = Field(
        default_factory=list,
        description="Durable facts that future turns should know independently of the narrative summary.",
    )


DEFAULT_CONTEXT_CONFIG = ContextBuilderConfig()


def build_llm_context(
    *,
    messages: Sequence[BaseMessage],
    system_messages: str | BaseMessage | Sequence[str | BaseMessage] | None = None,
    current_user_message: str | HumanMessage | None = None,
    conversation_summary: str | None = None,
    important_facts: str | Sequence[str] | None = None,
    long_term_memory: str | Sequence[str] | None = None,
    config: ContextBuilderConfig = DEFAULT_CONTEXT_CONFIG,
) -> list[BaseMessage]:
    

    system_block = _coerce_system_messages(system_messages)
    current_message = _coerce_current_user_message(current_user_message)
    history = _without_current_user_message(list(messages), current_message)

    full_context = [*system_block, *_memory_messages(long_term_memory), *history, *([current_message] if current_message else [])]

    ### if message count is below threshold, or if there is no cached context, return full context and if not pass whole messages 
    has_cached_context = bool(
        (conversation_summary and conversation_summary.strip())
        or _format_facts(important_facts, config.important_fact_limit)
    ) 

    if len(history) + (1 if current_message else 0) <= config.summary_threshold or not has_cached_context:
        return full_context

    recent_messages = _recent_human_ai_messages(history, limit=config.recent_message_limit)
    optimized: list[BaseMessage] = [*system_block]

    if conversation_summary and conversation_summary.strip():
        optimized.append(
            SystemMessage(
                content=(
                    "Conversation Summary\n"
                    "Use this as durable context from earlier turns:\n"
                    f"{conversation_summary.strip()}"
                )
            )
        )

    facts_text = _format_facts(important_facts, config.important_fact_limit)
    if facts_text:
        optimized.append(
            SystemMessage(
                content=(
                    "Important Facts\n"
                    "Preserve these facts unless the user explicitly corrects them:\n"
                    f"{facts_text}"
                )
            )
        )

    optimized.extend(_memory_messages(long_term_memory))

    if recent_messages:
        optimized.append(
            SystemMessage(
                content="Recent conversation messages follow. Historical tool outputs were intentionally omitted."
            )
        )
        optimized.extend(recent_messages)

    if current_message is not None:
        optimized.append(current_message)

    return optimized


def schedule_context_cache_refresh(
    *,
    app: Any,
    config: dict[str, Any],
    llm: Any,
    as_node: str | None = None,
    builder_config: ContextBuilderConfig = DEFAULT_CONTEXT_CONFIG,
) -> None:
    """Refresh cached context in the background without delaying the active response."""
    try:
        asyncio.create_task(
            refresh_context_cache(
                app=app,
                config=config,
                llm=llm,
                as_node=as_node,
                builder_config=builder_config,
            )
        )
    except RuntimeError:
        logger.exception("Unable to schedule context cache refresh")


async def refresh_context_cache(
    *,
    app: Any,
    config: dict[str, Any],
    llm: Any,
    as_node: str | None = None,
    builder_config: ContextBuilderConfig = DEFAULT_CONTEXT_CONFIG,
) -> None:
    try:
        state = await app.aget_state(config)
        values = getattr(state, "values", {}) or {}
        messages = values.get("messages", []) or []

        if len(messages) <= builder_config.summary_threshold:
            return

        summarized_count = int(values.get("summary_message_count") or 0)
        if len(messages) - summarized_count < builder_config.summary_min_new_messages:
            return

        update = await generate_context_cache_update(
            messages=messages,
            llm=llm,
            existing_summary=values.get("conversation_summary", ""),
            existing_facts=values.get("important_facts", []),
            builder_config=builder_config,
        )

        payload = {
            "conversation_summary": update.conversation_summary.strip(),
            "important_facts": update.important_facts[: builder_config.important_fact_limit],
            "summary_message_count": len(messages),
        }

        if as_node:
            await app.aupdate_state(config, payload, as_node=as_node)
        else:
            await app.aupdate_state(config, payload)
    except Exception:
        logger.exception("Context cache refresh failed")


async def generate_context_cache_update(
    *,
    messages: Sequence[BaseMessage],
    llm: Any,
    existing_summary: str | None = None,
    existing_facts: Sequence[str] | None = None,
    builder_config: ContextBuilderConfig = DEFAULT_CONTEXT_CONFIG,
) -> ContextCacheUpdate:
    transcript = _transcript_for_summary(messages, builder_config.summary_max_transcript_chars)
    facts_text = _format_facts(existing_facts, builder_config.important_fact_limit) or "None yet."
    summary_text = existing_summary.strip() if existing_summary else "None yet."

    prompt = [
        SystemMessage(
            content=(
                "You update cached conversation context for a production assistant.\n"
                "Do not produce generic summaries. Preserve user goals, completed tasks, decisions, "
                "assumptions, conclusions, and unresolved work.\n"
                "Keep Important Facts separate from the narrative summary.\n"
                "Do not include base64, image payloads, or raw tool output."
            )
        ),
        HumanMessage(
            content=(
                "Existing conversation summary:\n"
                f"{summary_text}\n\n"
                "Existing important facts:\n"
                f"{facts_text}\n\n"
                "New transcript to fold in:\n"
                f"{transcript}\n\n"
                "Return JSON with keys conversation_summary and important_facts."
            )
        ),
    ]

    try:
        structured_llm = llm.with_structured_output(ContextCacheUpdate)
        result = await structured_llm.ainvoke(prompt)
        if isinstance(result, ContextCacheUpdate):
            return _clean_cache_update(result, builder_config)
        if hasattr(result, "model_dump"):
            return _clean_cache_update(ContextCacheUpdate(**result.model_dump()), builder_config)
    except Exception:
        logger.exception("Structured context summary failed; falling back to JSON parsing")

    response = await llm.ainvoke(prompt)
    content = str(getattr(response, "content", "") or "")
    parsed = _parse_json_object(content)
    return _clean_cache_update(ContextCacheUpdate(**parsed), builder_config)


def _coerce_system_messages(
    system_messages: str | BaseMessage | Sequence[str | BaseMessage] | None,
) -> list[BaseMessage]:
    if system_messages is None:
        return []
    if isinstance(system_messages, (str, BaseMessage)):
        items: Iterable[str | BaseMessage] = [system_messages]
    else:
        items = system_messages

    result: list[BaseMessage] = []
    for item in items:
        if isinstance(item, BaseMessage):
            result.append(item)
        elif item and str(item).strip():
            result.append(SystemMessage(content=str(item).strip()))
    return result


def _coerce_current_user_message(current_user_message: str | HumanMessage | None) -> HumanMessage | None:
    if current_user_message is None:
        return None
    if isinstance(current_user_message, HumanMessage):
        return current_user_message
    content = str(current_user_message).strip()
    return HumanMessage(content=content) if content else None


def _without_current_user_message(
    messages: list[BaseMessage],
    current_message: HumanMessage | None,
) -> list[BaseMessage]:
    if current_message is None or not messages:
        return messages
    last = messages[-1]
    if isinstance(last, HumanMessage) and str(last.content).strip() == str(current_message.content).strip():
        return messages[:-1]
    return messages


def _recent_human_ai_messages(messages: Sequence[BaseMessage], *, limit: int) -> list[BaseMessage]:
    recent: list[BaseMessage] = []
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            recent.append(message)
        elif isinstance(message, AIMessage) and message.content and not getattr(message, "tool_calls", None):
            recent.append(message)
        if len(recent) >= limit:
            break
    recent.reverse()
    return recent


def _memory_messages(long_term_memory: str | Sequence[str] | None) -> list[SystemMessage]:
    memory_text = _format_facts(long_term_memory, settings.context_important_fact_limit)
    if not memory_text:
        return []
    return [
        SystemMessage(
            content=(
                "Long-Term Memory\n"
                "Use these durable memories when relevant:\n"
                f"{memory_text}"
            )
        )
    ]


def _format_facts(facts: str | Sequence[str] | None, limit: int) -> str:
    if facts is None:
        return ""
    if isinstance(facts, str):
        cleaned = facts.strip()
        return cleaned
    lines = []
    for fact in facts:
        text = str(fact).strip()
        if text:
            lines.append(f"- {text}")
        if len(lines) >= limit:
            break
    return "\n".join(lines)


def _transcript_for_summary(messages: Sequence[BaseMessage], max_chars: int) -> str:
    lines: list[str] = []
    for message in messages:
        if isinstance(message, ToolMessage):
            continue
        if isinstance(message, HumanMessage):
            role = "User"
        elif isinstance(message, AIMessage):
            if getattr(message, "tool_calls", None) and not message.content:
                continue
            role = "Assistant"
        else:
            continue

        content = _safe_text(message.content)
        if not content:
            continue
        lines.append(f"{role}: {content}")

    transcript = "\n\n".join(lines)
    if len(transcript) <= max_chars:
        return transcript
    return transcript[-max_chars:]


def _safe_text(content: Any) -> str:
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        text = " ".join(parts)
    else:
        text = str(content)

    text = " ".join(text.split())
    if "base64," in text or "data:image" in text:
        return "[image payload omitted]"
    return text[:4000]


def _parse_json_object(content: str) -> dict[str, Any]:
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in context summary response")
    return json.loads(content[start : end + 1])


def _clean_cache_update(
    update: ContextCacheUpdate,
    builder_config: ContextBuilderConfig,
) -> ContextCacheUpdate:
    facts: list[str] = []
    seen: set[str] = set()
    for fact in update.important_facts:
        cleaned = " ".join(str(fact).split()).strip()
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            facts.append(cleaned)
        if len(facts) >= builder_config.important_fact_limit:
            break

    return ContextCacheUpdate(
        conversation_summary=" ".join(update.conversation_summary.split()).strip(),
        important_facts=facts,
    )
