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

class UserCreate(BaseModel):
    name : str = Field(..., min_length=3, max_length=15)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    name : str

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"   ### i am sending this use it for authentication 

class TokenData(BaseModel):
    username: Optional[str] = None
