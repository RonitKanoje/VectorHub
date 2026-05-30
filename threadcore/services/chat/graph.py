from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langsmith import traceable
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from threadcore.core.config import settings
from threadcore.services.chat.prompts import prompt, prompt1, simple_chat_prompt
from threadcore.services.ingestion.pipeline import retrieve_answer


load_dotenv()

llm = ChatOllama(model=settings.ollama_chat_model, temperature=0)
duckduckgo_tool = DuckDuckGoSearchResults(region="us-en")
wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=3000)
)
tools = [duckduckgo_tool, wiki_tool]
tool_node = ToolNode(tools)


class StructuredAnswer(BaseModel):
    answer: str = Field(description="Final answer to the user")
    confidence: float = Field(description="Confidence from 0 to 1 that the answer is grounded in context")


class RouteDecision(BaseModel):
    decision: Literal["rag", "chat"] = Field(
        description="Decide whether to use the retrieval system or general chat knowledge."
    )


structured_llm = llm.with_structured_output(StructuredAnswer)
route_llm = llm.with_structured_output(RouteDecision)
tool_ready_llm = llm.bind_tools(tools)

CONFIDENCE_THRESHOLD = 0.5


class ChatState(TypedDict):
    user_message: str
    route: str
    messages: Annotated[list[BaseMessage], add_messages]
    context: list[str]
    meta: list[dict]
    confidence: float


def chat_node(state: ChatState):
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

    result: StructuredAnswer = structured_llm.invoke(messages)
    if result.confidence < CONFIDENCE_THRESHOLD:
        tool_response = tool_ready_llm.invoke(messages)
        return {"messages": [tool_response], "confidence": result.confidence}

    return {"messages": [AIMessage(content=result.answer)], "confidence": result.confidence}


@traceable(name="RAG Tool")
def rag_node(state: ChatState, config) -> dict:
    thread_id = config["configurable"]["thread_id"]
    user_id = config["configurable"]["user_id"]
    query = state["user_message"]

    result = retrieve_answer(query, user_id=user_id, thread_id=thread_id)
    contexts = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {"context": contexts, "meta": metadata}


def intent_node(state: ChatState):
    messages = [
        SystemMessage(content=prompt.template),
        HumanMessage(content=state["user_message"]),
    ]

    try:
        result: RouteDecision = route_llm.invoke(messages)
        route = result.decision
    except Exception:
        route = "chat"

    return {"route": route}


def confidence_tools_condition(state: ChatState):
    confidence = state.get("confidence", 1.0)
    if confidence >= CONFIDENCE_THRESHOLD:
        return END

    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return END


def simple_chat_node(state: ChatState):
    messages = state.get("messages", []).copy()
    if not messages:
        messages.append(SystemMessage(content=simple_chat_prompt.template))

    messages.append(HumanMessage(content=state["user_message"]))
    response = llm.invoke(messages)
    return {"messages": [response]}


def build_chatbot(checkpointer):
    graph = StateGraph(ChatState)
    graph.add_node("intent", intent_node)
    graph.add_node("simple_chat_node", simple_chat_node)
    graph.add_node("chat_node", chat_node)
    graph.add_node("rag_node", rag_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "intent")
    graph.add_conditional_edges(
        "intent",
        lambda state: state["route"],
        {
            "chat": "simple_chat_node",
            "rag": "rag_node",
        },
    )
    graph.add_edge("rag_node", "chat_node")
    graph.add_conditional_edges(
        "chat_node",
        confidence_tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )
    graph.add_edge("tools", "chat_node")

    return graph.compile(checkpointer=checkpointer)


def load_conversation(chatbot, thread_id: str):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
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
