from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from threadcore.core.config import settings
from threadcore.services.chat.prompts import name_chat_prompt


class TitleResponse(BaseModel):
    title: str = Field(description="A concise title for the chat conversation")


def title_from_message(message: BaseMessage) -> str:
    llm = ChatOllama(model=settings.ollama_chat_model, temperature=0)
    structured_llm = llm.with_structured_output(TitleResponse)
    response = structured_llm.invoke(name_chat_prompt.format(message=message.content))
    return response.title

