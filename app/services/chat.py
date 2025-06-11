from app.services.retriever import Retriever
from app.providers.gemini_embedder import genai
from app.config.settings import GEMINI_API_KEY

class ChatRAG:

    def __init__(self):
        self.retriever = Retriever(embedding_model="huggingface")  # Puedes cambiar al que quieras

        # Inicializamos Gemini (modo generación)
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

    def chat(self, question: str):
        # 1️ Recuperar contexto
        resultados = self.retriever.retrieve(question, top_k=5)
        contexto = "\n".join([res["text"] for res in resultados])

        # 2️ Preparar prompt
        prompt = f"""
Eres un asistente experto en documentación interna. Utiliza el siguiente contexto para responder:

Contexto:
{contexto}

Pregunta:
{question}

Respuesta:
"""

        # 3️Generar respuesta con Gemini
        respuesta = self.model.generate_content(prompt)
        return respuesta.text.strip()