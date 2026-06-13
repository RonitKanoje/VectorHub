from langchain_google_genai import ChatGoogleGenerativeAI

from threadcore.core.config import settings
from threadcore.services.chat.schemas import (
    PersonalMemoryDecision,
    RouteDecision,
    StructuredAnswer,
)


# Base LLM model
llm = ChatGoogleGenerativeAI(
    model=settings.gemini_chat_model,
    google_api_key=settings.gemini_api_key,
    temperature=0,
)

# Structured output variants
structured_llm = llm.with_structured_output(StructuredAnswer)
route_llm = llm.with_structured_output(RouteDecision)
personal_memory_llm = llm.with_structured_output(PersonalMemoryDecision)

# Tool-enabled variant
def get_tool_ready_llm(tools):
    """Get LLM with tools bound."""
    return llm.bind_tools(tools)


# Configuration constants
CONFIDENCE_THRESHOLD = 0.2