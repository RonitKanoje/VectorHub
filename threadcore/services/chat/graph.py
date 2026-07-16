from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from langsmith import traceable
from threadcore.services.chat.nodes import (
    chat_node,
    intent_node,
    personal_memory_node,
    rag_node,
    simple_chat_node,
    tool_node,
)
from threadcore.services.chat.schemas import ChatState
from threadcore.services.chat.tools_config import tool_executor

load_dotenv()


def tool_decision_condition(state: ChatState):
    if state["can_answer_without_tools"]:
        return END

    return "tool_node"


def intent_route(state: ChatState):
    """Route after intent detection."""
    if state["route"] == "rag":
        return "rag_node"
    return "simple_chat_node"


@traceable(name="Build Chatbot Graph")
def build_chatbot(checkpointer):

    graph = StateGraph(ChatState)

    # Nodes
    graph.add_node("intent", intent_node)
    graph.add_node("rag_node", rag_node)
    graph.add_node("simple_chat_node", simple_chat_node)
    graph.add_node("personal_memory_node", personal_memory_node)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tool_node", tool_node)
    graph.add_node("tools", tool_executor)

    # Start
    graph.add_edge(START, "intent")

    # Intent decides between chat and RAG
    graph.add_conditional_edges(
        "intent",
        intent_route,
        {
            "rag_node": "rag_node",
            "simple_chat_node": "simple_chat_node",
        },
    )

    # Personal memory always runs in parallel
    graph.add_edge("intent", "personal_memory_node")

    # Join before chat
    graph.add_edge(
        ["rag_node", "personal_memory_node"],
        "chat_node",
    )

    graph.add_edge(
        ["simple_chat_node", "personal_memory_node"],
        "chat_node",
    )

    # Tool decision routing
    graph.add_conditional_edges(
        "chat_node",
        tool_decision_condition,
        {
            "tool_node": "tool_node",
            END: END,
        },
    )

    # Tool execution
    graph.add_edge("tool_node", "tools")
    graph.add_edge("tools", "chat_node")

    compiled = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["tools"],
    )

    return compiled


def normalize_content(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(item.get("text", ""))

        return "".join(parts)

    return str(content)


async def load_conversation(chatbot, thread_id: str):

    state = await chatbot.aget_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if state is None:
        return []

    messages = state.values.get("messages", [])

    is_awaiting_tool_approval = (
        state.next is not None and "tools" in state.next
    )

    pending_tool_name: str | None = None
    pending_message_index: int | None = None

    if is_awaiting_tool_approval:
        for idx in range(len(messages) - 1, -1, -1):
            msg = messages[idx]
            if (
                msg.type == "ai"
                and hasattr(msg, "tool_calls")
                and msg.tool_calls
            ):
                pending_tool_name = msg.tool_calls[0].get("name") or msg.tool_calls[0].get("function", {}).get("name")
                pending_message_index = idx
                break

    conversation = []

    for idx, message in enumerate(messages):
        if message.type == "human":
            conversation.append(
                {
                    "role": "user",
                    "content": normalize_content(message.content),
                }
            )

        elif message.type == "ai":
            if message.tool_calls and not (
                is_awaiting_tool_approval
                and idx == pending_message_index
                and pending_tool_name
            ):
                continue

            entry: dict = {
                "role": "assistant",
                "content": normalize_content(message.content),
            }

            if (
                is_awaiting_tool_approval
                and idx == pending_message_index
                and pending_tool_name
            ):
                entry["requires_approval"] = True
                entry["tool"] = pending_tool_name

            conversation.append(entry)

    return conversation
