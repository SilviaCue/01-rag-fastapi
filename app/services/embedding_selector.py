from app.providers.gemini_embedder import get_embedding as gemini_embedding
from app.providers.hf_embedder import get_embedding as hf_embedding

class EmbeddingSelector:

    def __init__(self, model_name: str = "gemini"):
        self.model_name = model_name.lower()

    def get_embedding(self, text: str):
        if self.model_name == "gemini":
            return gemini_embedding(text)
        elif self.model_name == "huggingface":
            return hf_embedding(text)
        else:
            raise ValueError(f"Modelo de embedding no soportado: {self.model_name}")
