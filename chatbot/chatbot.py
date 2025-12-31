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
from typing import TypedDict,Annotated,Optional
from dotenv import load_dotenv
from langsmith import traceable
from langgraph.checkpoint.postgres import PostgresSaver
import os
from backend.main import main

load_dotenv()

llm = ChatOllama(model = "llama3.2")

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

def chatNode(state:ChatState):

    system_mesasge = SystemMessage(
        content=(
            "You are a helpful assistant that helps users in finding information if user asks anything related to the rag you have to use the tools to find the information. If user asks anything unrelated to the rag you have to politely refuse to answer that query. and you have to always provide source link for the information you provide.You can also use the tools to find information from the web or wikipedia. If you use any tool you have to mention that in your response."
        )
    )
    # messages = [system_mesasge,*state["messages"]]
    messages = [system_mesasge  + state["messages"]]
    response = llmWithTools.invoke(messages)
    return {"messages": state["messages"] + [response]}

## Tools
ddgo = DuckDuckGoSearchResults(region = "us-en")

wiki_tool = WikipediaQueryRun(
    WikipediaAPIWrapper=WikipediaAPIWrapper(
        top_k_results=1,
        doc_content_chars_max=3000
    )
)

def tool_node(query):
    """" Retrieve most relevant document from the retrieval system ."""

    result = main("vMGRbgXUEBQ",query)

    context = [pageCont for pageCont in result.page_content]
    meta = [metaData for metaData in result.metadata]

    return {
        "context": context,
        "meta": meta
    }


tools = [ddgo,tool_node,wiki_tool]

llmWithTools = llm.bind_tools(tools)

conn = psycopg.connect(
    os.getenv("DATABASE_URL"),autoccommit = True
)
checkpointer = PostgresSaver(conn=conn)

checkpointer.setup()


graph = StateGraph(ChatState)
graph.add_node("chatNode",chatNode)
graph.add_node("tools",tool_node)

graph.add_edge(START,chatNode)
graph.add_conditional_edges(chatNode,tool_node)
graph.add_edge(tool_node,chatNode)


# def retrieve_all_threads():
#     allThreads = set()
#     for checkpoint in checkpointer.list(None):
#         allThreads.add(
#             checkpoint.config["configurable"]["thread_id"]
#         )
#     return list(allThreads)

if __name__ == "__main__":
    CONFIG = {
        "configurable": {
            "thread_id": "test_thread_1"
        }
    }
    workflow = graph.compile(checkpointer=checkpointer,config=CONFIG)
    intial_state = {
        "messages" : "Where company database is discussed in this viseo"
    }
    result = workflow.invoke(intial_state)
    print(result["messages"][-1].content)
