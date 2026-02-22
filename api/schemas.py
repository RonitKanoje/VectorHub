from pydantic import BaseModel, Field
from typing import List, Optional

class processMedia(BaseModel):
    path : str = Field(..., description="file path to process")
    media : str = Field(..., description="Type of media: 'audio' or 'video'")
    thread_id : str = Field(..., description="Thread ID for chat context")
    language: Optional[str] = Field(None, description="Language of the media content")

class chatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender: 'user'")
    content: str = Field(..., description="Content of the message")
    thread_id: str = Field(..., description="Thread ID for chat context")

class chatName(BaseModel):
    message: str = Field(..., description="Content of the user message to generate a chat title from")
    thread_id: str = Field(..., description="Thread ID for chat context")
