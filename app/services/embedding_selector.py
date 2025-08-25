from app.providers.gemini_embedder import get_embedding as gemini_embedding
from app.providers.hf_embedder import get_embedding as hf_embedding
from app.config import settings

# Selector de modelo de embedding
class EmbeddingSelector:

    def __init__(self, model_name: str = None):
        # Usa el de configuración por defecto si no se pasa model_name
        self.model_name = (model_name or settings.EMBEDDING_MODEL).lower()
# Obtener el embedding según el modelo seleccionado
    def get_embedding(self, text: str):
        if self.model_name == "gemini":
            return gemini_embedding(text)
        elif self.model_name == "huggingface":
            return hf_embedding(text)
        else:
            raise ValueError(f"Modelo de embedding no soportado: {self.model_name}")
