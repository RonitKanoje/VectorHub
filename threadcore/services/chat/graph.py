from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from langsmith import traceable

from threadcore.services.chat.llm_config import CONFIDENCE_THRESHOLD
from threadcore.services.chat.nodes import (
    chat_node,
    intent_node,
    personal_memory_node,
    rag_node,
    simple_chat_node,
)
from threadcore.services.chat.schemas import ChatState
from threadcore.services.chat.tools_config import tool_node

load_dotenv()


def confidence_tools_condition(state: ChatState):
    """Determine if tools should be used based on confidence."""
    confidence = state.get("confidence", 1.0)

    if confidence >= CONFIDENCE_THRESHOLD:
        return END

    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return END

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
    graph.add_node("tools", tool_node)

    # Start
    graph.add_edge(START, "intent")

    # Intent decides between chat and rag
    graph.add_conditional_edges(
        "intent",
        intent_route,
        {
            "rag_node": "rag_node",
            "simple_chat_node": "simple_chat_node",
        },
    )

    # Memory always runs in parallel
    graph.add_edge("intent", "personal_memory_node")

    # Wait for BOTH:
    #   rag/simple_chat
    #        +
    # personal_memory
    graph.add_edge(
        ["rag_node", "personal_memory_node"],
        "chat_node",
    )

    graph.add_edge(
        ["simple_chat_node", "personal_memory_node"],
        "chat_node",
    )

    # Tool routing
    graph.add_conditional_edges(
        "chat_node",
        confidence_tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )

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
    """Load conversation history from checkpointed state.

    When the graph is paused at interrupt_before=['tools'], state.next contains
    ('tools',) and the last AIMessage has non-empty tool_calls but empty content.
    We detect this directly from the checkpoint — the canonical LangGraph source
    of truth — and annotate that message with requires_approval and the tool name,
    so the frontend can restore the approval UI after a page refresh.
    """

    state = await chatbot.aget_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if state is None:
        return []

    messages = state.values.get("messages", [])

    # Detect whether the graph is currently paused waiting for tool approval.
    # state.next is a tuple of node names the graph wants to execute next.
    is_awaiting_tool_approval = (
        state.next is not None and "tools" in state.next
    )

    # If paused, identify the specific tool that is pending by inspecting the
    # last AIMessage with tool_calls in the checkpoint. This is the message
    # chat_node returned before the interrupt fired.
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
            entry: dict = {
                "role": "assistant",
                "content": normalize_content(message.content),
            }

            # Annotate the specific interrupted message with approval metadata.
            # The frontend already knows how to render the approval card when
            # requires_approval=True is present — no placeholder text is needed.
            if (
                is_awaiting_tool_approval
                and idx == pending_message_index
                and pending_tool_name
            ):
                entry["requires_approval"] = True
                entry["tool"] = pending_tool_name

            conversation.append(entry)

    return conversation
