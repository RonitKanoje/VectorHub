"""
AnalystState — single source of truth for the entire analyst graph.

Key design decision:
  schema_ready  → gates whether the LLM agent is allowed to run tools.
                  It is False until the preprocessor+EDA nodes have populated
                  df_schema.  The agent node checks this flag before every
                  tool call so the LLM can never fabricate column names.
"""

from __future__ import annotations
from typing import Annotated, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AnalystState(TypedDict):
    # ── conversation ──────────────────────────────────────────────────────────
    messages: Annotated[list[BaseMessage], add_messages]

    # ── dataset ───────────────────────────────────────────────────────────────
    dataset_path: str          # path to the (cleaned) CSV on disk
    dataset_profile: dict[str, Any]  # cheap metadata from profiler.py (rows, cols,
                                     # missing %, memory) — populated before graph runs

    # ── pipeline flags ────────────────────────────────────────────────────────
    is_initialized: bool       # True once preprocessing+EDA have run once
    schema_ready: bool         # True only after df_schema is populated
                               # → LLM tool calls are BLOCKED until this is True

    # ── preprocessing artefacts ───────────────────────────────────────────────
    preprocessing_report: str  # JSON string produced by run_preprocessing()
    df_json: str               # first-50-rows JSON (for quick reference)

    # ── EDA artefacts ─────────────────────────────────────────────────────────
    eda_report: str            # JSON string with describe, dtypes, nulls, etc.

    # ── schema (injected into every tool call) ────────────────────────────────
    df_schema: dict[str, Any]  # {columns, dtypes, shape, sample_values}
                               # built once and reused for every follow-up

    # ── agent loop ────────────────────────────────────────────────────────────
    query_results: list[dict]  # accumulated tool outputs this turn
