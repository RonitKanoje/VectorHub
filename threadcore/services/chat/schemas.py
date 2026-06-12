"""Chat state and data schemas for the conversation graph."""

from typing import Annotated, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class StructuredAnswer(BaseModel):
    """LLM structured output for answered questions."""
    answer: str = Field(description="Final answer to the user")
    confidence: float = Field(
        description="Confidence from 0 to 1 that the answer is grounded in context"
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
