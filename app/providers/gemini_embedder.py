import google.generativeai as genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_embedding(text: str) -> list[float]:
    model = genai.GenerativeModel("models/embedding-001")
    response = model.embed_content(
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]
