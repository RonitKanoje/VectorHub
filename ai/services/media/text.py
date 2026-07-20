from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=10)
    return splitter.split_text(text)

