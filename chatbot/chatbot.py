from langchain_core.messages import SystemMessage,BaseMessage
import psycopg
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph import START,StateGraph,END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_ollama import ChatOllama
from typing import Annotated, Optional
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,AIMessage
from langsmith import traceable
import os 
from backend.main import retrieve_answer
from chatbot.prompt import prompt1

load_dotenv()

llm = ChatOllama(model = "llama3.2",temperature=0)

class ChatState(TypedDict):
    user_message: str
    messages: Annotated[list[BaseMessage], add_messages]
    context: list[str]
    meta: list[dict]
    tool_calls: int  # Added back

def chatNode(state: ChatState):
    tool_calls = state.get("tool_calls", 0)
    query = state["user_message"]
    context = state.get("context", [])
    meta = state.get("meta", [])
    context_text = "\n\n".join(context) if context else "No relevant context found."
    meta_data = (
        "\n".join(
            f"- Mentioned at {m['start']}s (duration {m['duration']}s)"
            for m in meta
        )
        if meta else
        "No timing metadata available."
    )
    
    # Build the messages for LLM invocation
    llm_messages = []
    
    # Always ensure system message is first if messages list is empty
    if not state.get("messages"):
        llm_messages.append(SystemMessage(content=prompt1.template))
    else:
        # If messages exist, use them (they should already have system message)
        llm_messages = state["messages"].copy()
    
    # Add the current human message with CLEAR INSTRUCTIONS
    human_message = HumanMessage(
        content=f"""IMPORTANT: First check if the context below answers the question. ONLY use external tools (Wikipedia, DuckDuckGo) if the context is insufficient or irrelevant.

Context from knowledge base:
{context_text}

Timing metadata (use ONLY for 'when/where' questions):
{meta_data}

User question: {query}

Instructions:
1. If the context above sufficiently answers the question, respond directly WITHOUT using tools
2. ONLY call external tools if you genuinely need additional information not in the context
3. Be efficient - avoid unnecessary tool calls"""
    )
    llm_messages.append(human_message)
    
    # Use LLM with or without tools based on tool call count
    if tool_calls >= 2:  # Maximum 2 tool calls - force final answer
        response = llm.invoke(llm_messages)
    else:
        response = llmWithTools.invoke(llm_messages)
    
    # Return only the NEW messages to be added
    return {
        "messages": [human_message, response],
        "tool_calls": tool_calls  # Preserve counter
    }


## Tools
ddgo = DuckDuckGoSearchResults(region = "us-en")

wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=1,
        doc_content_chars_max=3000
    )
)

@traceable(name = "RAG Tool")
def rag_node(state : ChatState,config) -> dict:
    """" Retrieve most relevant document from the retrieval system ."""

    thread_id = config["configurable"]["thread_id"]
    query = state['user_message']

    result = retrieve_answer(query, thread_id=thread_id)

    contexts = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        "context": contexts,    
        "meta": metadata
    }

# Wrapper function to increment tool counter
def tools_with_counter(state: ChatState):
    """Execute tools and increment the counter."""
    result = tool_node.invoke(state)
    return {
        **result,
        "tool_calls": state.get("tool_calls", 0) + 1
    }

tools = [ddgo,wiki_tool]
tool_node = ToolNode(tools)


llmWithTools = llm.bind_tools(tools)

# Checkpointer to save and load conversation states

def build_chatbot(checkpointer):
    graph = StateGraph(ChatState)

    graph.add_node("chatNode", chatNode)
    graph.add_node("ragNode", rag_node)
    graph.add_node("tools", tools_with_counter)  # Use wrapped version

    # User message → retrieve relevant docs first
    graph.add_edge(START, "ragNode")
    
    # After retrieval → LLM generates response
    graph.add_edge("ragNode", "chatNode")
    
    # LLM decides to use tools or end
    graph.add_conditional_edges(
        "chatNode",
        tools_condition,
        {
            "tools": "tools",
            END: END
        }
    )
    
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

    msgs = state.values.get("messages", [])
    # result = []

    # i = 0
    # n = len(msgs)

    # while i < n:
    #     msg = msgs[i]

    #     # Human message → always keep
    #     if msg.type == "human":
    #         result.append({
    #             "role": "user",
    #             "content": msg.content
    #         })

    #         i += 1

    #         # Consume all following AI messages
    #         last_ai = None
    #         while i < n and msgs[i].type == "ai":
    #             last_ai = {
    #                 "role": "assistant",
    #                 "content": msgs[i].content
    #             }
    #             i += 1

    #         # Append ONLY the final AI response
    #         if last_ai:
    #             result.append(last_ai)

    #     else:
    #         i += 1

    return msgs



if __name__ == '__main__':
    pass