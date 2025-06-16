import os
from app.services.retriever import Retriever
from app.config import settings
from app.services.generation_selector import GenerationSelector
from fastapi.responses import FileResponse

class ChatRAG:

    def __init__(self):
        self.retriever = Retriever(embedding_model=settings.EMBEDDING_MODEL)
        self.generator = GenerationSelector(settings.GENERATION_MODEL)
        self.upload_path = "storage/docs_raw"

    def chat(self, question: str):
        resultados = self.retriever.retrieve(question, top_k=5)
        contexto = "\n".join([res["text"] for res in resultados])

        prompt = f"""
Eres un asistente experto en documentación interna. Usa el siguiente contexto para responder:

Contexto:
{contexto}

Pregunta:
{question}

Respuesta:
"""

        respuesta = self.generator.generate(prompt)

        # Añadir enlaces si se mencionan nombres de archivo existentes
        for fname in os.listdir(self.upload_path):
            if fname.lower().endswith(".pdf") and fname.lower() in question.lower():
                url = f"http://127.0.0.1:8000/download/{fname}"
                respuesta += f"\n\nPuedes descargar el archivo '{fname}' aquí: {url}"
                break

        return respuesta
