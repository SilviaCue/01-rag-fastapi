# app/config/genai_client.py

import google.generativeai as genai
from app.config.secret_keys import GEMINI_API_KEY

def configure_genai():
    genai.configure(api_key=GEMINI_API_KEY)
