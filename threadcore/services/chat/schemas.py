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

    can_answer_without_tools: bool = Field(
        description=(
            "True if the user's request can be completely answered using only "
            "Personal Memory, RAG Context, and General Knowledge. False if "
            "external tools (DuckDuckGo, Wikipedia, etc.) are required.\n\n"
            "Return True for general knowledge, programming, reasoning, mathematics, "
            "or when Personal Memory or RAG Context answers the question.\n\n"
            "Return False for live information, current prices, weather, news, sports "
            "scores, currency exchange rates, explicit requests to search, or when "
            "the information is unavailable without external tools."
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
    can_answer_without_tools: bool
    conversation_summary: NotRequired[str]
    important_facts: NotRequired[list[str]]
    summary_message_count: NotRequired[int]
