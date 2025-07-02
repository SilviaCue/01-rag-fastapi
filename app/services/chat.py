
import os
import re
from app.services.retriever import Retriever
from app.config import settings
from app.services.generation_selector import GenerationSelector
from app.routers.vacaciones import contar_dias_vacaciones
from app.routers.vacaciones_drive import contar_dias_vacaciones_drive

# Versión local
from app.services.vacaciones_service import obtener_nombres_vacaciones

# Desde Google Drive (CSV)
from app.services.vacaciones_service_drive import obtener_nombres_vacaciones_drive as obtener_nombres_vacaciones

# Desde Google Calendar
from app.services.vacaciones_googlecalendar import obtener_vacaciones_desde_calendar as obtener_vacaciones_google_calendar


class ChatRAG:

    def __init__(self):
        self.retriever = Retriever()
        self.generator = GenerationSelector(settings.GENERATION_MODEL)
        self.upload_path = "storage/docs_raw"

    def chat(self, question: str):
        print("DEBUG fuentes activas:")
        print("Google Sheets:", settings.USAR_GOOGLE_SHEETS)
        print("Google Calendar:", settings.USAR_GOOGLE_CALENDAR)
        print("Excel Local:", settings.USAR_EXCEL_LOCAL)
        nombres_validos = obtener_nombres_vacaciones()
        print("Nombres detectados en el Excel:", nombres_validos)
        nombre_detectado = next((n for n in nombres_validos if n in question.lower()), None)

        # Configuración de fuente activa
        usar_google_sheets = settings.USAR_GOOGLE_SHEETS
        usar_google_calendar = settings.USAR_GOOGLE_CALENDAR
        usar_excel_local = settings.USAR_EXCEL_LOCAL

        try:
            # Opción 1: "¿Quién está de vacaciones hoy?"
            if "hoy" in question.lower() and "vacacion" in question.lower():
                if usar_google_calendar:
                    nombres_hoy = obtener_vacaciones_google_calendar()
                    if nombres_hoy:
                        return f"Hoy están de vacaciones: {', '.join(n.title() for n in nombres_hoy)}."
                    else:
                        return "Hoy no hay nadie marcado como de vacaciones en el calendario."
                else:
                    return "La fuente Google Calendar está desactivada."

            # Opción 2: Consultar vacaciones por persona
            if nombre_detectado and "vacacion" in question.lower():
                if usar_google_sheets:
                    datos = contar_dias_vacaciones_drive(nombre_detectado)
                    return (
                        f"{datos['persona']} tiene {datos['vacaciones_disfrutadas']} días de vacaciones disfrutadas, "
                        f"{datos['vacaciones_reservadas']} días de vacaciones reservadas, "
                        f"{datos['festivos_disfrutados']} festivos disfrutados, {datos['festivos_futuros']} festivos futuros, "
                        f"{datos['otros_permisos_disfrutados']} días por otros permisos disfrutados y "
                        f"{datos['otros_permisos_reservados']} días por otros permisos reservados. "
                        f"Además, tiene {datos['vacaciones_anteriores']} días de vacaciones del año anterior. "
                        f"Días restantes según calendario: {datos['restantes']}. "
                        f"En total hay {datos['total_marcados']} días marcados en el calendario."
                    )
                elif usar_excel_local:
                    datos = contar_dias_vacaciones(nombre_detectado)
                    return (
                        f"{datos['persona']} tiene {datos['dias_vacaciones']} días de vacaciones, "
                        f"{datos['festivos']} festivos y {datos['otros_permisos']} otros permisos. "
                        f"En total hay {datos['total_marcados']} días marcados en el calendario."
                    )
                elif usar_google_calendar:
                    nombres_hoy = obtener_vacaciones_google_calendar()
                    if nombre_detectado in nombres_hoy:
                        return f"{nombre_detectado.title()} está de vacaciones hoy, según el calendario."
                    else:
                        return f"{nombre_detectado.title()} no aparece como de vacaciones en el calendario de hoy."

                else:
                    return "No hay ninguna fuente activa para consultar vacaciones."

        except Exception as e:
            return f"Error al consultar los días de vacaciones: {str(e)}"

        # --- RAG normal ---
        resultados = self.retriever.retrieve(question, top_k=5)
        contexto = "\n".join([res["text"] for res in resultados])[:3000]

        prompt = f"""
Eres un asistente experto en la empresa idearium y documentación organizativa. Te encargas de redactar emails y responder a preguntas relacionadas con la empresa.

Tu tarea es:
- Leer cuidadosamente el contexto proporcionado.
- Responder de forma precisa, clara, natural y muy amable.
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

        # Si el usuario pide documentos
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
