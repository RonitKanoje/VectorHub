from dotenv import load_dotenv
from pathlib import Path
import os

# Force-load .env from project root
load_dotenv()

print("TRACING:", os.getenv("LANGCHAIN_TRACING_V2"))
print("PROJECT:", os.getenv("LANGCHAIN_PROJECT"))
print("API KEY:", os.getenv("LANGCHAIN_API_KEY"))
