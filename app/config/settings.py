
import os
from app.config.secret_keys import SecretKeys

secrets = SecretKeys()

# API KEYS
GEMINI_API_KEY = secrets.gemini_api_key
HUGGINGFACE_API_KEY = secrets.huggingface_api_key
OPENAI_API_KEY = secrets.openai_api_key

# CONFIGURACIÓN GENERAL
DOCS_RAW_PATH = os.getenv("DOCS_RAW_PATH", "storage/docs_raw")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))

# MODELOS SELECCIONABLES
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "huggingface")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini")



