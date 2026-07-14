from langchain_groq import ChatGroq

from threadcore.core.config import settings
from threadcore.services.chat.schemas import RouteDecision

llm = ChatGroq(
    model="llama-3.3-70b-versatile",   # or settings.groq_model
    api_key=settings.groq_api_key,
    temperature=0,
)

# Structured-output wrappers
route_llm = llm.with_structured_output(RouteDecision)

# Temporary: use the same Groq LLM for memory extraction
personal_memory_llm = llm.with_structured_output(RouteDecision)

# Configuration constants
CONFIDENCE_THRESHOLD = 0.2