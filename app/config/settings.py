import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DOCS_RAW_PATH = os.getenv("DOCS_RAW_PATH", "storage/docs_raw")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))



