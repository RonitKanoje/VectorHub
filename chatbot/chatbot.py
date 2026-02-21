from langchain_core.messages import SystemMessage, BaseMessage, HumanMessage, AIMessage
import psycopg
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_ollama import ChatOllama
from typing import Annotated, Optional,Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langsmith import traceable
import os 
from backend.main import retrieve_answer
from chatbot.prompt import prompt1,simple_chat_prompt,prompt
from pydantic import BaseModel, Field


load_dotenv()

# LLM
llm = ChatOllama(model="llama3.2", temperature=0)

## Tools
ddgo = DuckDuckGoSearchResults(region="us-en")

wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=1,
        doc_content_chars_max=3000
    )
)

tools = [ddgo, wiki_tool]
tool_node = ToolNode(tools)

class strAns(BaseModel):
    answer: str = Field(description="Final Answer to the user")
    confidence: float = Field(description="Confidence that the answer is from the context range from 0 to 1")

class IsRag(BaseModel):
    # The LLM can ONLY pick "rag" or "chat"
    decision: Literal["rag", "chat"] = Field(
        description="Decide whether to use the RAG search tool or general chat knowledge."
    )

structured_llm = llm.with_structured_output(strAns)

isRag_llm = llm.with_structured_output(IsRag)
llmWithTools = llm.bind_tools(tools)

CONFIDENCE_THRESHOLD = 0.5

class ChatState(TypedDict):
    user_message: str
    route : str
    messages: Annotated[list[BaseMessage], add_messages]
    context: list[str]
    meta: list[dict]
    tool_calls: int  
    confidence: float


def chatNode(state: ChatState):
    query = state["user_message"]
    context = state.get("context", [])
    meta = state.get("meta", [])

    context_text = "\n\n".join(context) if context else "No relevant context found."
    meta_data = (
        "\n".join(
            f"- Mentioned at {m['start']}s (duration {m['duration']}s)"
            for m in meta
        )
        if meta else "No timing metadata available."
    )

    messages = state.get("messages", []).copy()

    # System message ONCE
    if not messages:
        messages.append(SystemMessage(content=prompt1.template))

    # Always add a human message for this turn
    messages.append(
        HumanMessage(
            content=f"""Context (use only if relevant):
{context_text}

Timing metadata (ONLY for 'when/where' questions):
{meta_data}

User question:
{query}"""
        )
    )

    # First, get confidence score using structured output
    result: strAns = structured_llm.invoke(messages)
    confidence = result.confidence

    # If confidence is low, call LLM with tools to let it decide
    if confidence < CONFIDENCE_THRESHOLD:
        # Use the LLM with tools bound
        tool_response = llmWithTools.invoke(messages)
        
        return {
            "messages": [tool_response],
            "confidence": confidence
        }
    else:
        # High confidence - return the answer directly
        ai_message = AIMessage(content=result.answer)
        
        return {
            "messages": [ai_message],
            "confidence": confidence
        }


@traceable(name="RAG Tool")
def rag_node(state: ChatState, config) -> dict:
    """Retrieve most relevant document from the retrieval system."""

    thread_id = config["configurable"]["thread_id"]
    query = state['user_message']

    result = retrieve_answer(query, thread_id=thread_id)

    contexts = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        "context": contexts,    
        "meta": metadata
    }

def intent_node(state: ChatState):
    msg = [
        SystemMessage(content=prompt.template),
        HumanMessage(content=state["user_message"])
    ]

    try:
        result: IsRag = isRag_llm.invoke(msg)
        route = result.decision
    except Exception:
        route = "chat"   # safe fallback

    return {"route": route}


def confidence_tools_condition(state: ChatState):
    """Route based on confidence and tool calls in the message."""
    confidence = state.get("confidence", 1.0)
    
    # If high confidence, end immediately
    if confidence >= CONFIDENCE_THRESHOLD:
        return END
    
    # Low confidence - check if LLM wants to use tools
    last_message = state["messages"][-1]
    
    # Check if the message has tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:   ####check this 
        return "tools"
    
    return END

def simpleChatNode(state : ChatState):

    messages = state.get("messages", []).copy()

    if not messages:
        messages.append(SystemMessage(content = simple_chat_prompt.template))

    messages.append(HumanMessage(content=state["user_message"]))

    response = llm.invoke(messages)

    return {
        "messages" : [response]
    }


# Checkpointer to save and load conversation states
def build_chatbot(checkpointer):
    graph = StateGraph(ChatState)

    graph.add_node("intent",intent_node)
    graph.add_node("simpleChatNode",simpleChatNode)
    graph.add_node("chatNode", chatNode)
    graph.add_node("ragNode", rag_node)
    graph.add_node("tools", tool_node)

    # User message → retrieve relevant docs first
    graph.add_edge(START, "intent")

    graph.add_conditional_edges(
        "intent",
        lambda s : s['route'],
        {
            "chat": "simpleChatNode",
            "rag" : "ragNode"
        }
    )
    
    # After retrieval → LLM generates response
    graph.add_edge("ragNode", "chatNode")
    
    # LLM decides to use tools or end based on confidence
    graph.add_conditional_edges(
        "chatNode",
        confidence_tools_condition,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # After tools execute, go back to chatNode to process results
    graph.add_edge("tools", "chatNode")
    
    return graph.compile(checkpointer=checkpointer)

#Defining functions to retrieve all threads and load conversation
def retrieve_all_threads(checkpointer):
    allThreads = []
    seen = set()

    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config["configurable"]["thread_id"]
        if thread_id not in seen:
            seen.add(thread_id)
            allThreads.append(thread_id)

    return allThreads


def loadConv(chatBot, thread_id):
    state = chatBot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if state is None:
        return []

    msgs = state.values.get("messages", [])
    result = []

    for msg in msgs:
        if msg.type == "human":
            result.append({
                "role": "user",
                "content": msg.content
            })

        elif msg.type == "ai":
            result.append({
                "role": "assistant",
                "content": msg.content
            })

    return result

if __name__ == '__main__':
    pass