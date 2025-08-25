
import google.generativeai as genai
from app.config.settings import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
# Función para obtener embeddings usando Gemini
def get_embedding(text: str) -> list[float]:
    try:
        response = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return response["embedding"]
    except Exception as e:
        print(" Error en Gemini embedding:", e)
        return []


