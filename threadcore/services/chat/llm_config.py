"""LLM initialization and configuration."""

from langchain_ollama import ChatOllama

from threadcore.core.config import settings
from threadcore.services.chat.schemas import RouteDecision, StructuredAnswer


# Base LLM model
llm = ChatOllama(model=settings.ollama_chat_model, temperature=0)

# Structured output variants
structured_llm = llm.with_structured_output(StructuredAnswer)
route_llm = llm.with_structured_output(RouteDecision)

# Tool-enabled variant
def get_tool_ready_llm(tools):
    """Get LLM with tools bound."""
    return llm.bind_tools(tools)


# Configuration constants
CONFIDENCE_THRESHOLD = 0.5
