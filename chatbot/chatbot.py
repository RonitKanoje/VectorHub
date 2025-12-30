from langchain_core.messages import SystemMessage,BaseMessage
import psycopg
from langchain_core.tools import tool,DuckDuckGoSearchResults,WikipediaQueryRun
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
from backend.embeddings import retriveEmbed

load_dotenv()

llm = ChatOllama(model = "llama3.2")

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

def chatNode(state:ChatState):

    system_mesasge = SystemMessage(
        content=(
            "You are a helpful assistant"
        )
    )
    # messages = [system_mesasge,*state["messages"]]
    messages = [system_mesasge]   #### see you havn't added user message here yet
    response = llmWithTools.invoke(messages)
    return response

## Tools
ddgo = DuckDuckGoSearchResults(region = "us-en")

wiki_tool = WikipediaQueryRun(
    WikipediaAPIWrapper=WikipediaAPIWrapper(
        top_k_results=1,
        doc_content_chars_max=3000
    )
)

def tool_node(query):
    """" Retrieve most relevant document from the retrieval"""

    result = retriveEmbed.invoke(query)
    print(result)
    ### see in which format you are getting the data then return 


tools = [ddgo,tool_node,wiki_tool]

llmWithTools = llm.bind_tools(tools)

conn = psycopg.connect(
    os.getenv("DATABASE_URL"),autoccommit = True
)
checkpointer = PostgresSaver(conn=conn)



graph = StateGraph(ChatState)
graph.add_node("chatNode",chatNode)
graph.add_node("tools",tool_node)

graph.add_edge(START,chatNode)
graph.add_conditional_edges(chatNode,tool_node)
graph.add_edge(tool_node,chatNode)


def retrieve_all_threads():
    allThreads = set()
    for checkpoint in checkpointer.list(None):
        allThreads.add(
            checkpoint.config["configurable"]["thread_id"]
        )
    return list(allThreads)