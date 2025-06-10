# app/test/debug_model_attributes.py
import google.generativeai as genai
from app.config.settings import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.get_model("models/embedding-001")

print("🔍 Atributos del modelo:")
print(dir(model))
