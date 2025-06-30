import os
import re
from app.services.retriever import Retriever
from app.config import settings
from app.services.generation_selector import GenerationSelector
from app.services.vacaciones_service import obtener_nombres_vacaciones
from app.routers.vacaciones import contar_dias_vacaciones  # <-- Import directo aquí

class ChatRAG:

    def __init__(self):
        self.retriever = Retriever()
        self.generator = GenerationSelector(settings.GENERATION_MODEL)
        self.upload_path = "storage/docs_raw"

    def chat(self, question: str):
        nombres_validos = obtener_nombres_vacaciones()
        print("Nombres detectados en el Excel:", nombres_validos)
        nombre_detectado = next((n for n in nombres_validos if n in question.lower()), None)

        if nombre_detectado and "vacacion" in question.lower():
            try:
                # Ahora llamada directa, sin requests ni HTTP interno:
                datos = contar_dias_vacaciones(nombre_detectado)
                return (
                    f"{datos['persona']} tiene {datos['dias_vacaciones']} días de vacaciones, "
                    f"{datos['festivos']} festivos y {datos['otros_permisos']} otros permisos. "
                    f"En total hay {datos['total_marcados']} días marcados en el calendario."
                )
            except Exception as e:
                return f"Error al consultar los días de vacaciones: {str(e)}"

        # --- RAG NORMAL (esto no cambia nada) ---
        resultados = self.retriever.retrieve(question, top_k=5)
        contexto = "\n".join([res["text"] for res in resultados])[:3000]

        prompt = f"""
Eres un asistente experto en la empresa idearium y documentación organizativa. Te encargagas de redactar emails y responder a preguntas relacionadas con la empresa.

Tu tarea es:
- Leer cuidadosamente el contexto proporcionado.
- Responder de forma precisa, clara , natural y muy amable.
- No inventar información que no aparezca en el contexto.
- Indicar si no hay suficiente información en los documentos.

CONTEXT (fragmentos relevantes extraídos de la documentación):
\"\"\"{contexto}\"\"\"

PREGUNTA DEL USUARIO:
\"{question}\"

INSTRUCCIONES:
- Si el contexto responde claramente a la pregunta, explica la respuesta de forma ordenada y amable.
- Si el contexto solo ofrece información parcial, acláralo e intenta ayudar al usuario.
- Si no encuentras información suficiente, indícalo directamente y sugiere revisar el documento correspondiente o volver a subirlo.

RESPUESTA:
"""

        try:
            respuesta = self.generator.generate(prompt)
        except Exception as e:
            respuesta = f"Error al generar respuesta: {str(e)}"

        # Si el usuario pide documentos (esto no cambia nada)
        if any(x in question.lower() for x in ["descargar", "pdf", "documento"]):
            documentos_utilizados = {res["document_id"] for res in resultados}
            for doc in documentos_utilizados:
                nombre_archivo = os.path.basename(doc)
                for ext in [".pdf", ".docx"]:
                    if not nombre_archivo.endswith(ext):
                        archivo_con_ext = f"{nombre_archivo}{ext}"
                    else:
                        archivo_con_ext = nombre_archivo

                    ruta_completa = os.path.join(self.upload_path, archivo_con_ext)
                    if os.path.isfile(ruta_completa):
                        url = f"http://127.0.0.1:8000/download/{archivo_con_ext}"
                        respuesta += f"\n\nPuedes descargar el documento '{archivo_con_ext}' aquí: {url}"
                        break

        return respuesta
