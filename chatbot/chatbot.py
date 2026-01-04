from langchain_core.messages import SystemMessage,BaseMessage
import psycopg
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph import START,StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_ollama import ChatOllama
from typing import Annotated, Optional
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langsmith import traceable
import os
from backend.main import retrieve_answer
import requests
from chatbot.prompt import prompt1

load_dotenv()

llm = ChatOllama(model = "llama3.2",temperature=0)

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]
    thread_id : str


def chatNode(state: ChatState):
    messages = state["messages"]

    if not messages or not isinstance(messages[0], SystemMessage):
        system_message = SystemMessage(
            content=prompt1.format()
        )
        messages = [system_message] + messages

    response = llmWithTools.invoke(messages)

    return {
        "messages": messages + [response]
    }

## Tools
ddgo = DuckDuckGoSearchResults(region = "us-en")

wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=1,
        doc_content_chars_max=3000
    )
)

@tool
@traceable(name = "RAG Tool")
def rag_node(state : ChatState,query: str) -> dict:
    """" Retrieve most relevant document from the retrieval system ."""

    thread_id = state["thread_id"]

    result = retrieve_answer(query, thread_id=thread_id)

    contexts = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        "context": contexts,
        "meta": metadata
    }

tools = [rag_node]
llmWithTools = llm.bind_tools(tools)
tool_node = ToolNode(tools)


llmWithTools = llm.bind_tools(tools)


# Checkpointer to save and load conversation states
# chatbot/chatbot.py

def build_chatbot(checkpointer):
    graph = StateGraph(ChatState)

    graph.add_node("chatNode", chatNode)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chatNode")
    graph.add_conditional_edges("chatNode", tools_condition)
    graph.add_edge("tools", "chatNode")

    return graph.compile(checkpointer=checkpointer)


#Defining functions to retrieve all threads and load conversation
def retrieve_all_threads(checkpointer):
    allThreads = set()
    for checkpoint in checkpointer.list(None):
        allThreads.add(
            checkpoint.config["configurable"]["thread_id"]
        )
    return list(allThreads)

def loadConv(chatBot ,thread_id):
    state = chatBot.get_state(
        config={
            "configurable": {
                "thread_id": thread_id
            }
        })
    return state.values.get("messages", [])

if __name__ == '__main__':
    pass