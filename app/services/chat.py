import os
import re
from datetime import datetime, date, timedelta
from app.services.retriever import Retriever  # Para RAG general, no calendar
from app.config import settings
from app.services.generation_selector import GenerationSelector
from app.routers.vacaciones import contar_dias_vacaciones
from app.routers.vacaciones_drive import contar_dias_vacaciones_drive

# Versiones locales y externas
from app.services.vacaciones_service import obtener_nombres_vacaciones
from app.services.vacaciones_service_drive import obtener_nombres_vacaciones_drive as obtener_nombres_vacaciones
from app.services.vacaciones_googlecalendar import (
    obtener_lista_nombres_desde_calendar,
    obtener_periodos_evento,
    filtrar_por_semana,  
    filtrar_por_dia 
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
        semana_actual = date.today().isocalendar()[1]
        anio_actual = date.today().year
        pregunta_lower = question.lower()
        semana = None
        # --- Filtro lógico de eventos por semana/día (nivel de negocio)
        # Estos filtros definen qué eventos deben incluirse en el análisis según la pregunta del usuario.
        # Se aplican antes de generar la respuesta, para reducir el conjunto de eventos relevantes
        
        if "esta semana" in pregunta_lower:
            semana = semana_actual
            anio = anio_actual
        elif "la semana que viene" in pregunta_lower or "semana que viene" in pregunta_lower:
            semana = semana_actual + 1
            anio = anio_actual
        
        dia = None
        if "hoy" in pregunta_lower:
            dia = datetime.today().date()
        elif "mañana" in pregunta_lower:
            dia = (datetime.today() + timedelta(days=1)).date()

        # Configuración de fuente activa
        usar_google_sheets = settings.USAR_GOOGLE_SHEETS
        usar_google_calendar = settings.USAR_GOOGLE_CALENDAR
        usar_excel_local = settings.USAR_EXCEL_LOCAL

        # --- Detección tipo de evento:
        if any(pal in pregunta_lower for pal in ["reunion", "reuniones", "meeting", "cita"]):
            tipo_evento = "reuniones"
        elif any(pal in pregunta_lower for pal in ["festivo", "festivos", "fiesta", "fiestas"]):
            tipo_evento = "festivos"
        elif any(pal in pregunta_lower for pal in ["entrega", "entregas", "deadline", "sprint"]):
            tipo_evento = "entregas"
        else:
            tipo_evento = "vacaciones"

        # --- Si no hay nombre, pero se pregunta por reuniones/festivos, forzar nombre_detectado = "todos"
        if not nombre_detectado and tipo_evento in ["reuniones", "festivos", "entregas"]:
            nombre_detectado = "todos"

        try:
            if nombre_detectado:
                print("Pregunta recibida:", question)
                print("Nombre detectado:", nombre_detectado)
                print("Tipo de evento:", tipo_evento)
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
                    resumen_dias = obtener_periodos_evento(
                        nombre_detectado, tipo_evento=tipo_evento, anio=anio
                    )
                    if tipo_evento == "entregas" and "siguiente" in pregunta_lower:
                        resumen_dias =sorted(resumen_dias, key=lambda x: x[0])
                        hoy= datetime.today().date()
                        for evento in resumen_dias:
                            fecha_evento =evento[0].date() if isinstance(evento[0],datetime) else evento[0]
                            if fecha_evento > hoy:
                                resumen_dias =[evento]
                                break
                            else:
                                resumen_dias =[]
                            
                    if semana:
                        resumen_dias = filtrar_por_semana(resumen_dias, anio, semana)
                        print(f"Aplicando filtro por semana: {semana}, año: {anio}")
                    if dia:
                        resumen_dias = filtrar_por_dia(resumen_dias, dia)
                        print(f"{len(resumen_dias)} eventos recuperados antes de filtrar")


                    match_mes = re.search(r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)", pregunta_lower)
                    mes = None
                    if match_mes:
                        mes_nombre = match_mes.group(1)
                        meses = {
                            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                            "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
                        }
                        mes = meses[mes_nombre]
                    if not resumen_dias:
                        if semana:
                            return f"No hay {tipo_evento} programadas para la semana {semana} del año {anio}."
                        elif dia:
                            return f"No hay {tipo_evento} programadas para el día {dia.strftime('%d/%m/%Y')}."
                        elif mes:
                            return f"No hay {tipo_evento} programadas para el mes de {mes_nombre} del año {anio}."
                        else:
                            return f"No hay {tipo_evento} registrados para {nombre_detectado.capitalize()} en el año {anio}."
                    
                    respuesta = responder_con_gemini(
                        nombre_detectado, resumen_dias, self.generator, tipo_evento=tipo_evento, anio=anio,mes=mes
                    )
                    return respuesta
                else:
                    return "No hay ninguna fuente de vacaciones activa."

        except Exception as e:
            return f"Error al consultar los días de vacaciones: {str(e)}"

        # Si no es pregunta de vacaciones, usa RAG normal
        resultados = self.retriever.retrieve(question, top_k=12)
        contexto = "\n".join([res["text"] for res in resultados])[:4000]

        prompt = f"""
Eres un asistente experto en la empresa Idearium y documentación organizativa. Tu tarea es responder de forma muy amable, profesional y basada SOLO en el contexto proporcionado. NO inventes información. Tienes que responder a preguntas relacionadas con la empresa.

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
- Si la pregunta es para dar la bienvenida a una nueva persona (palabras clave: bienvenida, onboarding, incorporación, nuevo/a compañero/a, bienvenida a [nombre]), redacta un email claro y profesional dirigido a esa persona, SOLO con la información real encontrada en el contexto (manual de OnBoarding y fragmentos recuperados).
- Organiza el email de bienvenida en estos bloques claros (omite los que falten en el contexto):
    • Quiénes somos y a qué nos dedicamos
    • Valores de la empresa
    • Modalidad de trabajo y dirección de la oficina
    • Horarios y fichaje horario (enlace o pasos si aparecen)
    • Calendario y cómo se solicitan vacaciones/festivos (incluye enlaces si aparecen)
    • Accesos importantes: correo, Google Calendar, repositorios, etc.
    • Otros recursos: enlaces, emails de contacto, reuniones online, etc.
- Usa siempre un tono cercano, profesional y claro.
- Si falta algún dato importante (lo ves en el índice pero no está en el contenido), dilo amablemente y sugiere revisar el manual adjunto o contactar con RRHH.
- NO inventes, NO rellenes huecos: utiliza exclusivamente la información real recuperada aquí. Resume bien los puntos clave y no repitas textos innecesarios.
- Termina el email con una despedida cordial y ofrece ayuda para cualquier duda.
- Estructura el email con saludo inicial, resumen práctico y despedida profesional y amable.

Ejemplo de estructura de email (ajusta el nombre según la pregunta):
Asunto: Bienvenida a Idearium, Ana

Hola Ana:

Te damos la bienvenida a Idearium. Aquí tienes la información clave para tu incorporación:

- Horario y fichaje: ...
- Vacaciones y festivos: ...
- Accesos importantes: ...
- Otros recursos: ...

Si necesitas más información, consulta el Manual de Bienvenida o contacta con RRHH.

Un saludo cordial,
El equipo de Idearium
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
