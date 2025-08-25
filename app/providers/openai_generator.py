import openai
from app.config.settings import OPENAI_API_KEY
# Proveedor para generación de texto usando OpenAI
class OpenAIGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.model = "gpt-4o"  # se puede cambiar por otro modelo de OpenAI
# Función para generar texto usando OpenAI
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
