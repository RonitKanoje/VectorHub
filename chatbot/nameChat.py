from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from chatbot.prompt import nameChat_prompt
from pydantic import BaseModel, Field

class responseModel(BaseModel):
    title: str = Field(description="A concise title for the chat conversation")


def title_from_message(message: BaseMessage) -> str:

    llm = ChatOllama(model="llama3.2", temperature=0)

    structured_llm = llm.with_structured_output(responseModel)

    response = structured_llm.invoke(nameChat_prompt.format(message=message))
    return response.title