# app/config/genai_client.py
import google.generativeai as genai
from app.config.settings import GEMINI_API_KEY

def configure_genai():
    genai.configure(api_key=GEMINI_API_KEY)
