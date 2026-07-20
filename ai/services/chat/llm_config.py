from langchain_groq import ChatGroq

from ai.core.config import settings
from ai.services.chat.schemas import MemoryReconciliationDecision, RouteDecision , PersonalMemoryDecision

llm = ChatGroq(
    model="llama-3.3-70b-versatile",   # or settings.groq_model
    api_key=settings.groq_api_key,
    temperature=0,
)

# Structured-output wrappers
route_llm = llm.with_structured_output(RouteDecision)
memory_reconciliation_llm = llm.with_structured_output(
    MemoryReconciliationDecision
)

# Temporary: use the same Groq LLM for memory extraction
personal_memory_llm = llm.with_structured_output(PersonalMemoryDecision)

