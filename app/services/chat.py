import os
from app.services.retriever import Retriever
from app.config import settings
from app.services.generation_selector import GenerationSelector
from fastapi.responses import FileResponse

class ChatRAG:

    def __init__(self):
        self.retriever = Retriever()  # SIN argumentos aquí
        self.generator = GenerationSelector(settings.GENERATION_MODEL)
        self.upload_path = "storage/docs_raw"

    def chat(self, question: str):
        resultados = self.retriever.retrieve(question, top_k=5)
        contexto = "\n".join([res["text"] for res in resultados])

        MAX_CONTEXT_LENGTH = 3000
        contexto = contexto[:MAX_CONTEXT_LENGTH]

        prompt = f"""
Eres un asistente muy amable y especializado en normativa y documentación interna que trabaja en Idearium. 

Busca la información varias veces hasta que la encuentres y no te inventes nada. Usa el siguiente contexto para responder:

Contexto:
{contexto}

Pregunta:
{question}

Respuesta:
"""

        try:
            respuesta = self.generator.generate(prompt)
        except Exception as e:
            respuesta = f"Error al generar respuesta: {str(e)}"

        for fname in os.listdir(self.upload_path):
            if fname.lower().endswith(".pdf") and fname.lower() in question.lower():
                url = f"http://127.0.0.1:8000/download/{fname}"
                respuesta += f"\n\nPuedes descargar el archivo '{fname}' aquí: {url}"
                break

        return respuesta
