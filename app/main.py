# app/main.py
from fastapi import FastAPI
from app.routers import upload  # puedes ir agregando los demás luego

app = FastAPI(title="RAG API")

# Registrar rutas
app.include_router(upload.router)






