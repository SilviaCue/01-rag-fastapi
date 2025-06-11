# app/main.py
from fastapi import FastAPI
from app.routers import upload, chat # puedes ir agregando los demás luego
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="RAG API",
    version="0.1.0"
)
from app.config.genai_client import configure_genai

# Inicializa la API de Gemini al arrancar el servidor
configure_genai()

# Configurar CORS para permitir acceso desde Swagger y cualquier origen (por ahora)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir esto luego para mayor seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(upload.router)
app.include_router(chat.router)
