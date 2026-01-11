from langchain_text_splitters import RecursiveCharacterTextSplitter
from langsmith import traceable

@traceable(name = "Text Splitting")
def split(text):

    splitter = RecursiveCharacterTextSplitter(chunk_size = 150,chunk_overlap = 10)
    chunks = splitter.split_text(text)
    return chunks
