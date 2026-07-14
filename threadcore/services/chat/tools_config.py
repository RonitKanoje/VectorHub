"""Tools configuration for the chatbot."""

from langchain_community.tools import DuckDuckGoSearchResults, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.prebuilt import ToolNode


# Initialize tools
duckduckgo_tool = DuckDuckGoSearchResults(region="us-en")

wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=3000)
)

tools = [duckduckgo_tool, wiki_tool]

# Create tool executor node
tool_executor = ToolNode(tools)
