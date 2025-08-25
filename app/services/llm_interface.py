from app.model_selector import get_current_model
from app.providers import gemini_embedder  # futuros: openai_embedder, hf_embedder


# Interfaz para obtener embeddings usando el modelo seleccionado
def get_embedding(text: str) -> list[float]:
    model = get_current_model()
    if model == "gemini":
        return gemini_embedder.get_embedding(text)
    else:
        raise ValueError(f"Modelo '{model}' no está soportado aún.")
