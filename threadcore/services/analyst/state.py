from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AnalystState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # conversation history
    dataset_path: str
    df_json: str           # first 50 rows as JSON (used by agents)
    preprocessing_report: str
    eda_report: str
    insight_queries: list[str]   # pandas query strings proposed by insight_agent
    query_results: list[str]     # string results of executing those queries
    is_initialized: bool         # True after first preprocessing+EDA pass
