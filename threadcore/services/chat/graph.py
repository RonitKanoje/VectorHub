from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
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
    if confidence >= CONFIDENCE_THRESHOLD :
        return END

    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return END


def intent_route_branches(state: ChatState):
    if state["route"] == "rag":
        return ["rag_node", "personal_memory_node"]  
    return ["simple_chat_node", "personal_memory_node"]


@traceable(name="Build Chatbot Graph")
def build_chatbot(checkpointer):
    graph = StateGraph(ChatState)

    graph.add_node("intent", intent_node)
    graph.add_node("personal_memory_node", personal_memory_node)
    graph.add_node("simple_chat_node", simple_chat_node)
    graph.add_node("rag_node", rag_node)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "intent")

    #Both branches run in parallel after intent
    graph.add_conditional_edges(
        "intent",
        intent_route_branches,
        ["rag_node", "simple_chat_node", "personal_memory_node"],
    )

    #rag_node and personal_memory_node both feed into chat_node
    graph.add_edge(["rag_node", "personal_memory_node"], "chat_node")

    # simple_chat also waits for personal_memory_node
    graph.add_edge(["simple_chat_node", "personal_memory_node"], END)

    graph.add_conditional_edges(
        "chat_node",
        confidence_tools_condition,
        {"tools": "tools", END: END},
    )
    graph.add_edge("tools", "chat_node")

    return graph.compile(checkpointer=checkpointer, interrupt_before=["tools"])


async def load_conversation(chatbot, thread_id: str):
    """Load conversation history from checkpointed state."""
    state = await chatbot.aget_state(config={"configurable": {"thread_id": thread_id}})
    if state is None:
        return []

    messages = state.values.get("messages", [])
    conversation = []

    for message in messages:
        if message.type == "human":
            conversation.append({"role": "user", "content": message.content})
        elif message.type == "ai":
            conversation.append({"role": "assistant", "content": message.content})

    return conversation
