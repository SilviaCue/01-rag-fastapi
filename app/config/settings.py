
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


# CONFIGURACIÓN DE FUENTES DE VACACIONES
#USAR_GOOGLE_SHEETS = bool(secrets.usar_google_sheets)
USAR_GOOGLE_CALENDAR = bool(secrets.usar_google_calendar)

# emails para alertas
ALERT_EMAILS = secrets.alert_emails




# settings.py
# Configuración global del proyecto.
#
# Este archivo reúne y organiza todas las opciones importantes para el funcionamiento de la API:
#
# 1. Carga las claves de acceso a los modelos de IA (Gemini, HuggingFace, OpenAI) usando la clase SecretKeys,
#    que obtiene los valores desde secret_keys.json.
#
# 2. Define rutas y parámetros generales, como la carpeta donde se guardan los documentos subidos (DOCS_RAW_PATH)
#    y el tamaño de los fragmentos de texto a procesar (CHUNK_SIZE).
#
# 3. Permite elegir el modelo de embeddings y el modelo de generación de texto que se usará en cada momento,
#    mediante variables de entorno (EMBEDDING_MODEL, GENERATION_MODEL).
#
# 4. Centraliza la selección de la fuente para los datos de vacaciones (Google Calendar, Google Sheets o Excel local),
#    también con variables que pueden ser modificadas en secret_keys.json o como variables de entorno.
#
# Gracias a este archivo, se puede cambiar la configuración global del sistema (como modelos, rutas y origen de datos)
# sin modificar el resto del código, facilitando la personalización y el despliegue en distintos entornos.
