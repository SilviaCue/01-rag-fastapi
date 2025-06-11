import google.generativeai as genai

class GeminiGenerator:

    def __init__(self):
        self.model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text.strip()




