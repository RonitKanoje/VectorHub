from __future__ import annotations
from typing import Annotated, Any
from typing_extensions import NotRequired, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AnalystState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    dataset_path: str          # path to the (cleaned) CSV on disk
    dataset_profile: dict[str, Any]  # cheap metadata from profiler.py (rows, cols, missing %, memory) — populated before graph runs
    is_initialized: bool       # True once preprocessing+EDA have run once
    schema_ready: bool         # True only after df_schema is populated LLM tool calls are BLOCKED until this is True  
    preprocessing_report: str  # JSON string produced by run_preprocessing()
    df_json: str               # first-50-rows JSON (for quick reference)
    eda_report: str            # JSON string with describe, dtypes, nulls, etc. 
    df_schema: dict[str, Any]  # {columns, dtypes, shape, sample_values} built once and reused for every follow-up 
    query_results: list[dict]  # accumulated tool outputs this turn
    conversation_summary: NotRequired[str]
    important_facts: NotRequired[list[str]]
    summary_message_count: NotRequired[int]
