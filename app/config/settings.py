import os
from app.config.secret_keys import SecretKeys

secrets = SecretKeys()

GEMINI_API_KEY = secrets.gemini_api_key
HUGGINGFACE_API_KEY = secrets.huggingface_api_key
OPENAI_API_KEY = secrets.openai_api_key

DOCS_RAW_PATH = os.getenv("DOCS_RAW_PATH", "storage/docs_raw")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
