_current_model = "gemini"  # valor por defecto

def set_model(name: str):
    global _current_model
    _current_model = name

def get_current_model():
    return _current_model
