from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar los routers
from app.routers import upload, chat, download, upload_one, upload_multiple, status, vacaciones #<-- Aquí cargas todos los routers que tienes

# Gemini config
from app.config.genai_client import configure_genai

from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title="RAG API",
    version="0.1.0"
)

# Inicializa Gemini al arrancar el servidor
configure_genai()

# Configurar CORS (por ahora abierto)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(download.router)
app.include_router(upload_one.router)
app.include_router(upload_multiple.router)
app.include_router(status.router)
app.include_router(vacaciones.router)


@app.get("/")
def root():
    return {
        "message": "Bienvenido a la API RAG. Visita /docs para ver la documentación interactiva."
    }


