from langchain_google_genai import ChatGoogleGenerativeAI

from threadcore.core.config import settings
from threadcore.services.chat.gemini_memory_client import GeminiPersonalMemoryLLM
from threadcore.services.chat.schemas import RouteDecision


llm = ChatGoogleGenerativeAI(
    model=settings.gemini_memory_model,
    temperature=0,
)

# Structured-output wrappers — created once and reused across all nodes.
route_llm = llm.with_structured_output(RouteDecision)


# Dedicated Gemini client for personal-memory extraction.
personal_memory_llm = GeminiPersonalMemoryLLM()

# Configuration constants
CONFIDENCE_THRESHOLD = 0.8
