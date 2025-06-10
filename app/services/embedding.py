from app.services.llm_interface import get_embedding

def generate_embedding(text: str):
    return get_embedding(text)
