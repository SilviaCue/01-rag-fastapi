from app.providers.gemini_embedder import get_embedding as gemini_embed
# from app.providers.openai_embedder import get_embedding as openai_embed
# from app.providers.huggingface_embedder import get_embedding as hf_embed

# Estado interno
_current_model = "gemini"  # por defecto

# Setter / Getter
def set_model(name: str):
    global _current_model
    _current_model = name

def get_current_model():
    return _current_model

# Selector de función según modelo actual
def get_embedding_function():
    if _current_model == "gemini":
        return gemini_embed
    elif _current_model == "openai":
        raise NotImplementedError("OpenAI aún no está implementado.")
    elif _current_model == "huggingface":
        raise NotImplementedError("HuggingFace aún no está implementado.")
    else:
        raise ValueError(f"Modelo desconocido: {_current_model}")
