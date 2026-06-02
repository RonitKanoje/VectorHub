from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProcessMediaRequest(BaseModel):
    path: str = Field(..., description="File path or content to process")
    media: Literal["youtube", "audio", "video", "text"]
    thread_id: str = Field(..., description="Thread ID for chat context")
    language: str | None = Field(default=None, description="Language of the media content")


class ChatMessageRequest(BaseModel):
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")
    thread_id: str = Field(..., description="Thread ID for chat context")


class ChatNameRequest(BaseModel):
    message: str = Field(..., description="Content of the user message")
    thread_id: str = Field(..., description="Thread ID for chat context")


class ThreadResponse(BaseModel):
    thread_id: str
    title: str

    model_config = ConfigDict(from_attributes=True)
