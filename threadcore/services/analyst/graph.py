from __future__ import annotations
import json
import logging
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session
from threadcore.domains.analyst.models import DatasetDB
from threadcore.services.analyst.profiler import format_profile_message, profile_dataset
from threadcore.services.analyst.state import AnalystState
from threadcore.services.analyst.nodes import (analyst_agent,eda_agent,preprocessor_agent,synthesis_agent)

logger = logging.getLogger(__name__)

# Router
def route_after_start(state: AnalystState) -> str:

    if state.get("is_initialized") and state.get("schema_ready"):
        return "analyst_agent"
    return "preprocessor_agent"

# Graph definition

def build_workflow() -> StateGraph:

    workflow = StateGraph(AnalystState)

    workflow.add_node("preprocessor_agent", preprocessor_agent)
    workflow.add_node("eda_agent", eda_agent)
    workflow.add_node("analyst_agent", analyst_agent)
    workflow.add_node("synthesis_agent", synthesis_agent)

    workflow.add_conditional_edges(
        START,
        route_after_start,
        {
            "preprocessor_agent": "preprocessor_agent",
            "analyst_agent": "analyst_agent",
        },
    )

    workflow.add_edge("preprocessor_agent", "eda_agent")
    workflow.add_edge("eda_agent", "analyst_agent")
    workflow.add_edge("analyst_agent", "synthesis_agent")
    workflow.add_edge("synthesis_agent", END)

    return workflow


def build_analyst_app(checkpointer=None):
    workflow = build_workflow()
    return workflow.compile(checkpointer=checkpointer)


# Compiled without checkpointer — injected at call-time via config
analyst_app = build_analyst_app()


def get_initial_analyst_state(message: str, dataset_path: str, dataset_profile: dict) -> AnalystState:
    """Build the initial state dict for the analyst workflow."""
    return {
        "messages":             [HumanMessage(content=message)],
        "dataset_path":         dataset_path,
        "dataset_profile":      dataset_profile,
        "df_json":              "",
        "preprocessing_report": "",
        "eda_report":           "",
        "df_schema":            {},
        "query_results":        [],
        "is_initialized":       False,
        "schema_ready":         False,
    }


async def load_analyst_conversation(analyst_app, thread_id: str, x_user_id: str) -> list[dict]:
    """Load and parse the analyst conversation history from the checkpointer."""
    config = {
        "configurable": {
            "thread_id": f"analyst-{x_user_id}-{thread_id}"
        }
    }

    state = await analyst_app.aget_state(config)

    if state is None or not state.values.get("messages"):
        return []

    messages = state.values["messages"]
    conversation = []

    current_assistant: dict | None = None

    def _flush(block: dict | None):
        """Add the current assistant block to conversation if it has content."""
        if block and (block["content"] or block["visualizations"]):
            conversation.append(block)

    for i, msg in enumerate(messages):
        logger.debug(
            "Analyst message[%s]: type=%s class=%s name=%s content=%s",
            i,
            msg.type,
            type(msg),
            getattr(msg, "name", None),
            msg.content,
        )

    for message in messages:
        if message.type == "human":
            _flush(current_assistant)
            current_assistant = {"role": "assistant", "content": "", "visualizations": []}
            conversation.append({"role": "user", "content": message.content})

        elif message.type == "ai":
            if current_assistant is None:
                current_assistant = {"role": "assistant", "content": "", "visualizations": []}
            # Only the final AIMessage (no tool_calls) carries the human-readable answer
            if message.content and not message.tool_calls:
                current_assistant["content"] += message.content

        elif message.type == "tool":
            if current_assistant is None:
                current_assistant = {"role": "assistant", "content": "", "visualizations": []}
            tool_name = getattr(message, "name", "") or ""
            if tool_name == "visualization_tool":
                try:
                    vis_data = json.loads(message.content)
                    if isinstance(vis_data, dict) and vis_data.get("type") == "visualization":
                        current_assistant["visualizations"].append(vis_data)
                except Exception:
                    pass

    _flush(current_assistant)

    return conversation
