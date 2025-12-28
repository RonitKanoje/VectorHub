from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import SystemMessage,BaseMessage
from langchain_core.tools import tool
from langgraph.graph import START,StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_ollama import OllamaLLM
from typing import TypedDict,Annotated,Optional

llm = OllamaLLM(model = "llama3.2")

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
    response = llm.invoke(messages)
    return response


def tool_node():
    return 

graph = StateGraph(ChatState)
graph.add_node("chatNode",chatNode)
graph.add_node("tools",tool_node)

graph.add_edge(START,chatNode)
graph.add_conditional_edges(chatNode,tool_node)
graph.add_edge(tool_node,chatNode)



