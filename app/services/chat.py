import os
import re
from app.services.retriever import Retriever
from app.config import settings
from app.services.generation_selector import GenerationSelector
from app.routers.vacaciones import contar_dias_vacaciones
from app.routers.vacaciones_drive import contar_dias_vacaciones_drive

# Versiones locales y externas
from app.services.vacaciones_service import obtener_nombres_vacaciones
from app.services.vacaciones_service_drive import obtener_nombres_vacaciones_drive as obtener_nombres_vacaciones
from app.services.vacaciones_googlecalendar import (
    obtener_vacaciones_desde_calendar as obtener_vacaciones_google_calendar,
    obtener_periodos_vacaciones,
    obtener_lista_nombres_desde_calendar,
)
from app.services.chat_utils import responder_con_gemini

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

        # Detectar nombres válidos desde la fuente activa
        if settings.USAR_GOOGLE_CALENDAR:
            nombres_validos_original = obtener_lista_nombres_desde_calendar()
        else:
            nombres_validos_original = obtener_nombres_vacaciones()

        nombres_validos = [n.lower() for n in nombres_validos_original]
        print("Nombres detectados desde la fuente activa:", nombres_validos)

        pregunta_lower = question.lower()
        nombre_detectado = next((n for n in nombres_validos if re.search(rf'\b{re.escape(n)}\b', pregunta_lower)), None)

        # --- Detecta año en la pregunta (por ejemplo, "2024", "2025", etc)
        match_anio = re.search(r"(20\d{2})", pregunta_lower)
        anio = int(match_anio.group(1)) if match_anio else 2025  # 2025 por defecto

        # Configuración de fuente activa
        usar_google_sheets = settings.USAR_GOOGLE_SHEETS
        usar_google_calendar = settings.USAR_GOOGLE_CALENDAR
        usar_excel_local = settings.USAR_EXCEL_LOCAL

        try:
            if "hoy" in pregunta_lower and any(pal in pregunta_lower for pal in ["vacacion", "vacaciones"]):
                if usar_google_calendar:
                    nombres_hoy = obtener_vacaciones_google_calendar()
                    if nombres_hoy:
                        return f"Hoy están de vacaciones: {', '.join(n.title() for n in nombres_hoy)}."
                    else:
                        return "Hoy no hay nadie marcado como de vacaciones en el calendario."
                else:
                    return "La fuente Google Calendar está desactivada."

            if nombre_detectado and any(pal in pregunta_lower for pal in ["vacacion", "vacaciones", "ausencia", "permiso"]):
                print("Pregunta recibida:", question)
                print("Nombre detectado:", nombre_detectado)
                print("Fuente activa: Google Sheets:", usar_google_sheets)
                print("Fuente activa: Google Calendar:", usar_google_calendar)
                print("Fuente activa: Excel Local:", usar_excel_local)

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
                    # --- SOLO ESTA LÍNEA: pasa el año detectado
                    periodos = obtener_periodos_vacaciones(nombre_detectado, anio=anio)
                    print(f"[DEBUG] Periodos de vacaciones encontrados para {nombre_detectado} ({anio}): {periodos}")
                    return responder_con_gemini(nombre_detectado, periodos, self.generator)
                else:
                    return "No hay ninguna fuente de vacaciones activa."

        except Exception as e:
            return f"Error al consultar los días de vacaciones: {str(e)}"

        resultados = self.retriever.retrieve(question, top_k=5)
        contexto = "\n".join([res["text"] for res in resultados])[:3000]

        prompt = f"""
Eres un asistente experto en la empresa Idearium y documentación organizativa. Tu tarea es responder de forma amable, profesional y basada SOLO en el contexto proporcionado. NO inventes información. Tienes que responder a preguntas relacionadas con la empresa.

Tu tarea es:
- Leer cuidadosamente el contexto proporcionado.
- Responder de forma precisa, clara, natural y muy amable.
- No inventar información que no aparezca en el contexto.
- Indicar si no hay suficiente información en los documentos.

CONTEXT (fragmentos relevantes extraídos de la documentación):
\"\"\"{contexto}\"\"\"  

PREGUNTA DEL USUARIO:
\"{question}\"

INSTRUCCIONES GENERALES:
- Si el contexto responde claramente a la pregunta, explica la respuesta de forma ordenada y amable.
- Si el contexto solo ofrece información parcial, acláralo e intenta ayudar al usuario.
- Si no encuentras información suficiente, indícalo directamente y sugiere revisar el documento correspondiente o volver a subirlo.


INSTRUCCIONES PARA EMAIL DE BIENVENIDA Y ONBOARDING:
- Si la pregunta es para dar la bienvenida a una nueva persona (palabras clave: bienvenida, onboarding, incorporación, nuevo/a compañero/a), redacta un email claro y profesional dirigido a esa persona, SOLO con la información real encontrada en el contexto (manual de OnBoarding y fragmentos recuperados).
- Lee atentamente todo el contexto recuperado, identifica y utiliza todos los apartados importantes: modalidad de trabajo (presencial, teletrabajo o mixto), dirección de la oficina, horarios, calendario, fichaje, procedimiento para pedir vacaciones/festivos, accesos, enlaces útiles, correo electrónico y cuentas, así como cualquier otro dato esencial de bienvenida.
- Si aparecen enlaces en el contexto, inclúyelos en el email. Si hay instrucciones concretas (por ejemplo, para acceder a una herramienta o solicitar acceso), indícalas en el texto.
- Si el contexto es fragmentario o falta información que parece importante (por ejemplo, ves referencias en el índice pero no ves el contenido), indícalo amablemente y sugiere revisar el manual de bienvenida o consultar a Recursos Humanos para más detalles.
- NO inventes, NO rellenes huecos: utiliza exclusivamente la información real recuperada aquí. Resume bien los puntos clave y no repitas textos innecesarios.
- Estructura el email con saludo inicial, resumen práctico y despedida profesional y amable.


Ejemplo de saludo inicial:
"Asunto: Bienvenida a Idearium, Ana.
Hola Ana:
Te damos la bienvenida a Idearium. Aquí tienes la información clave para tus primeros días..."


INSTRUCCIONES ESPECIALES PARA VACACIONES (Google Calendar):
- Calcula el total de días laborables de vacaciones (excluye fines de semana si es posible).
- Muestra cada periodo de vacaciones con fecha exacta de inicio y de fin, ambas incluidas.
- Asegúrate de que el día de inicio sea el primer día en que comienza el descanso, y el de fin, el último día que incluye el permiso.
- Resume al final la cantidad total de días laborables disfrutados.

🔹 Ejemplo de respuesta deseada:
"Silvia ha disfrutado de un total de 4 días laborables de vacaciones en 2025. 
- Del 12 al 14 de junio (3 días laborables).
- El 15 de mayo (1 día).

Actualmente no tiene más vacaciones registradas para este año."
"""

        try:
            respuesta = self.generator.generate(prompt)
        except Exception as e:
            respuesta = f"Error al generar respuesta: {str(e)}"

        if any(x in pregunta_lower for x in ["descargar", "pdf", "documento"]):
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
