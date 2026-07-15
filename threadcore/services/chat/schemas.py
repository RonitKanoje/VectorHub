"""Chat state and data schemas for the conversation graph."""

from typing import Annotated, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import NotRequired, TypedDict



class StructuredAnswer(BaseModel):
    """
    Structured response produced by chat_node before tool routing.
    """

    answer: str = Field(
        description=(
            "The best answer that can be generated using only the available "
            "Personal Memory, RAG Context, and General Knowledge. "
            "Do not assume external tools or live information are available."
        )
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "A confidence score between 0.0 and 1.0 representing how confident "
            "you are that the user's request can be completely answered WITHOUT "
            "using external tools.\n\n"
            "Use HIGH confidence (0.8-1.0) when:\n"
            "- Personal Memory fully answers the question.\n"
            "- RAG Context fully answers the question.\n"
            "- General knowledge is sufficient.\n"
            "- Programming, reasoning, mathematics, or explanatory questions.\n\n"
            "Use MEDIUM confidence (0.4-0.7) when:\n"
            "- The available information is only partially sufficient.\n"
            "- Some assumptions would be required.\n\n"
            "Use LOW confidence (0.0-0.3) when:\n"
            "- Current or live information is required.\n"
            "- News, weather, sports scores, stock prices, gold prices, or "
            "currency exchange rates are requested.\n"
            "- The user explicitly asks to search the web, DuckDuckGo, or Wikipedia.\n"
            "- External verification is required.\n"
            "- The required information is missing from Personal Memory, RAG Context, "
            "and General Knowledge.\n\n"
            "This score is used ONLY for deciding whether external tools should be "
            "invoked. It is NOT a measure of how grammatically correct or well-written "
            "the answer is."
        ),
    )

class RouteDecision(BaseModel):
    """LLM structured output for routing decisions."""
    decision: Literal["rag", "chat"] = Field(
        description="Decide whether to use the retrieval system or general chat knowledge."
    )


class PersonalMemoryDecision(BaseModel):
    """LLM structured output for personal-memory handling."""
    should_store: bool = Field(
        description="Whether the user message contains durable personal information to remember."
    )
    facts: list[str] = Field(
        default_factory=list,
        description="Concise first-person facts from the user message worth remembering.",
    )
    should_retrieve: bool = Field(
        description="Whether answering the message may require stored personal information."
    )


class ChatState(TypedDict):
    """State management for the conversation graph."""
    user_message: str
    route: str
    messages: Annotated[list[BaseMessage], add_messages]
    context: list[str]
    meta: list[dict]
    personal_context: list[str]
    stored_personal_facts: list[str]
    confidence: float
    conversation_summary: NotRequired[str]
    important_facts: NotRequired[list[str]]
    summary_message_count: NotRequired[int]
