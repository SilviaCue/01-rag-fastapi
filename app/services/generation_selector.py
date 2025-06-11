from app.providers.gemini_generator import GeminiGenerator
# Más adelante podríamos añadir: OpenAIGenerator, HFGenerator, etc.

class GenerationSelector:

    def __init__(self, model_name: str = "gemini"):
        self.model_name = model_name.lower()

        if self.model_name == "gemini":
            self.generator = GeminiGenerator()
        else:
            raise ValueError(f"Modelo de generación no soportado: {self.model_name}")

    def generate(self, prompt: str) -> str:
        return self.generator.generate(prompt)
