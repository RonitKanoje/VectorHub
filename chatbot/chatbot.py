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
from langgraph.checkpoint.postgres import PostgresSaver
import os
from backend.main import retrieve_answer

load_dotenv()

llm = ChatOllama(model = "llama3.2",temperature=0)

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

def chatNode(state:ChatState):

    system_mesasge = SystemMessage(
        content=(
            "You are a helpful assistant that helps users in finding information if user asks anything related to the rag you have to use the tools to find the information. If user asks anything unrelated to the rag you have to politely refuse to answer that query. and you have to always provide source link for the information you provide.You can also use the tools to find information from the web or wikipedia. If you use any tool you have to mention that in your response.   Use rag context to answer the user's question.  first try to find the answer from the rag context if you don't find it then use the tools to find the answer."
        )
    )
    messages = [system_mesasge,*state["messages"]]
    response = llmWithTools.invoke(messages)
    return {"messages": state["messages"] + [response]}

## Tools
ddgo = DuckDuckGoSearchResults(region = "us-en")

wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=1,
        doc_content_chars_max=3000
    )
)

@tool
def rag_node(query: str) -> dict:
    """" Retrieve most relevant document from the retrieval system ."""

    result = retrieve_answer(query)

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


conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname= os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

conn.autocommit = True

checkpointer = PostgresSaver(conn=conn)

checkpointer.setup()


graph = StateGraph(ChatState)
graph.add_node("chatNode",chatNode)
graph.add_node("tools",tool_node)

graph.add_edge(START,"chatNode")
graph.add_conditional_edges("chatNode",tools_condition)
graph.add_edge("tools","chatNode")


chatBot = graph.compile(checkpointer=checkpointer)

#Defining functions to retrieve all threads and load conversation
def retrieve_all_threads():
    allThreads = set()
    for checkpoint in checkpointer.list(None):
        allThreads.add(
            checkpoint.config["configurable"]["thread_id"]
        )
    return list(allThreads)

def loadConv(thread_id):
    state = chatBot.get_state(
        config={
            "configurable": {
                "thread_id": thread_id
            }
        })
    return state.values.get("messages", [])


if __name__ == "__main__":
    CONFIG = {
        "configurable": {
            "thread_id": "test_thread_2"
        }
    }
    

    initial_state = {
    "messages": [HumanMessage(content="Where company database is discussed in this video use rag to find the answer.") ]
    }
    workflow = graph.compile(checkpointer=checkpointer)
    result = workflow.invoke(
    initial_state,
    config={
        "configurable": {
            "thread_id": "test_thread_3"
            }
        }
    )
    print(result["messages"][-1].content)
