from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class ProcessMediaRequest(BaseModel):
    path: str = Field(..., description="File path or content to process")
    media: Literal["youtube", "audio", "video", "text", "document"]
    thread_id: str = Field(..., description="Thread ID for chat context")
    language: str | None = Field(default=None, description="Language of the media content")


class ChatMessageRequest(BaseModel):
    role: str = Field(default="user", description="Role of the message sender")
    content: str = Field(
        ...,
        validation_alias=AliasChoices("content", "message", "text", "query"),
        description="Content of the message",
    )
    thread_id: str = Field(
        ...,
        validation_alias=AliasChoices("thread_id", "threadId"),
        description="Thread ID for chat context",
    )
    is_tool_approval: bool = Field(default=False, description="Whether this is a tool approval resumption")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("content", "thread_id")
    @classmethod
    def required_string(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value


class ChatNameRequest(BaseModel):
    message: str = Field(..., description="Content of the user message")
    thread_id: str = Field(..., description="Thread ID for chat context")


class ThreadResponse(BaseModel):
    thread_id: str
    title: str

    model_config = ConfigDict(from_attributes=True)
