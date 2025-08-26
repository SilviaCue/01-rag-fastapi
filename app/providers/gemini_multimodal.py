import google.generativeai as genai
from app.config.settings import GEMINI_API_KEY
from PIL import Image

class GeminiMultimodalExtractor:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        # usamos el mismo modelo Pro multimodal
        self.model = genai.GenerativeModel("gemini-1.5-pro-002")

    def extract_text(self, file_path: str) -> str:
        """
        Extrae texto de una imagen o página escaneada usando Gemini multimodal.
        """
        try:
            # Abrir imagen (PIL garantiza formato compatible)
            image = Image.open(file_path)

            prompt = """Extrae TODO el texto del documento escaneado.
            - El documento está en español.
            - Devuelve únicamente el texto plano, sin inventar nada.
            """

            response = self.model.generate_content([prompt, image])

            return response.text.strip() if response.text else ""

        except Exception as e:
            print(f"Error en Gemini multimodal: {e}")
            return ""
