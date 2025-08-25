from app.providers.gemini_generator import GeminiGenerator
from app.providers.openai_generator import OpenAIGenerator
# Selector de modelo de generación
class GenerationSelector:
    def __init__(self, model_name: str = "gemini"):
        self.model_name = model_name.lower()

        if self.model_name == "gemini":
            self.generator = GeminiGenerator()
        elif self.model_name == "openai":
            self.generator = OpenAIGenerator()
        else:
            raise ValueError(f"Modelo de generación no soportado: {self.model_name}")
# Obtener generación según el modelo seleccionado
    def generate(self, prompt: str) -> str:
        return self.generator.generate(prompt)


