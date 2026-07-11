from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from threadcore.services.chat.llm_config import llm
from threadcore.services.chat.prompts import name_chat_prompt


class TitleResponse(BaseModel):
    title: str = Field(description="A concise title for the chat conversation")


# Created once at module load — reuses the shared base LLM from llm_config
_title_llm = llm.with_structured_output(TitleResponse)


def title_from_message(message: BaseMessage) -> str:
    response = _title_llm.invoke(name_chat_prompt.format(message=message.content))
    return response.title