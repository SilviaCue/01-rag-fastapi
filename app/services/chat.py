from app.services.retriever import Retriever
from app.config import settings
from app.services.generation_selector import GenerationSelector

class ChatRAG:

    def __init__(self):
        self.retriever = Retriever(embedding_model=settings.EMBEDDING_MODEL)
        self.generator = GenerationSelector(settings.GENERATION_MODEL)

    def chat(self, question: str):
        resultados = self.retriever.retrieve(question, top_k=5)
        contexto = "\n".join([res["text"] for res in resultados])

        prompt = f"""
Eres un asistente experto en documentación interna. Utiliza el siguiente contexto para responder:

Contexto:
{contexto}

Pregunta:
{question}

Respuesta:
"""

        respuesta = self.generator.generate(prompt)
        return respuesta
