# app/config/genai_client.py
import google.generativeai as genai
from app.config.settings import GEMINI_API_KEY


def configure_genai():
    print("Configurando Gemini...")
    if not GEMINI_API_KEY:
        raise ValueError("Falta la variable GEMINI_API_KEY en el entorno")
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini configurado correctamente.")
