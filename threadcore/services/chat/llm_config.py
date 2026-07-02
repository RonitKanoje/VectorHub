from langchain_ollama import ChatOllama

from threadcore.core.config import settings
from threadcore.services.chat.gemini_memory_client import GeminiPersonalMemoryLLM
from threadcore.services.chat.schemas import (
    PersonalMemoryDecision,
    RouteDecision,
    StructuredAnswer,
)

# Base LLM model
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)


# Structured output variants
structured_llm = llm.with_structured_output(StructuredAnswer)
route_llm = llm.with_structured_output(RouteDecision)
personal_memory_llm = GeminiPersonalMemoryLLM()

# Tool-enabled variant
def get_tool_ready_llm(tools):
    """Get LLM with tools bound."""
    return llm.bind_tools(tools)


# Configuration constants
CONFIDENCE_THRESHOLD = 0.2