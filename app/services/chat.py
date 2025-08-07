# Importaciones librerías necesarias del sistema, fechas y módulos propios del proyecto
import os
import re
from datetime import datetime, date, timedelta
# Importaciones de los módulos del proyecto
from app.services.retriever import Retriever  # Encargado de buscar fragmentos relevantes en los documentos
from app.config import settings # Configuración general
from app.services.generation_selector import GenerationSelector # Decide qué modelo usar para generar texto
# Funciones para leer nombres y eventos del calendarios
from app.services.vacaciones_googlecalendar import (
    obtener_lista_nombres_desde_calendar, # función para sacar los nombres
    obtener_periodos_evento, # función para sacar los eventos de calendario
    filtrar_por_semana,  # función para quedarte solo con eventos de cierta semana
    filtrar_por_dia  #función para quedarte solo con eventos de un día
)
# Función para generar respuestas usando IA (Gemini)
from app.services.chat_utils import responder_con_gemini

# Función que crea eventos en Google Calendar
from app.services.calendar_create import crear_evento_en_calendar

# Clase principal del sistema de chat
class ChatRAG:
    def __init__(self):
        self.retriever = Retriever() # Para buscar fragmentos de texto relevantes
        self.generator = GenerationSelector(settings.GENERATION_MODEL)# Para generar respuestas con IA
        self.upload_path = "storage/docs_raw" # Carpeta donde están los documentos subidos

    def chat(self, question: str):
        pregunta_lower = question.lower()
        pregunta_lower_reformulada = pregunta_lower  # Se usará luego

        # # --- Detección de intención de creación de evento (antes de reformular con Gemini)
        es_intencion_crear = any(
            pal in pregunta_lower for pal in [
                "crear", "añadir", "añade", "crea", "quiero", "me gustaria", "pon", "poner", "agenda", "agendar", "programa", "programar"
            ]
        )
        # Guarda la pregunta original tal cual, por si no hay que reformular para seguir con el flujo normal
        pregunta_reformulada = question  #pregunta del usuario original 
        # --- Reformulación automática de la pregunta con Gemini SOLO si hay intención de crear evento ---
        if es_intencion_crear:
            try:
                prompt_reformulacion = f"""
                Reformula la siguiente solicitud para crear un evento de calendario. Es MUY importante que respondas exactamente en este formato (no inventes nada, respeta el formato, nunca incluyas fecha ni hora en el título):
                Reformula esta solicitud en una frase clara, directa y sin ambigüedad, ideal para que un sistema automático la entienda y extraiga los datos (título, tipo de evento, fecha y hora) mediante expresiones regulares.
                IMPORTANTE:
                - La frase debe contener todos los datos: título, tipo de evento, fecha y hora, en ese orden.
                - No uses palabras genéricas como 'llamada', 'evento', ni añadas paréntesis innecesarios.
                - Al final de la frase, añade en una línea separada: 
                IMPORTANTE ACERCA DE TITULO_CALENDARIO:  [QUE EL TITULO CONTENGA UNICAMENTE UNA PALABRA]
                Ejemplo:
                Entrada: Pon una reunión que se llame chatRAG para el jueves 23 de julio a las 10
                Salida:
                Reunión chatRAG el jueves 23 de julio a las 10:00
                TITULO_CALENDARIO: chatRAG (Importante que el titulo sea una palabra sola y no añadas nada más) 
                
                Entrada: "{question}"
                Salida:"""

                # Llama a Gemini para generar la frase reformulada (ya limpia y en formato fácil de extraer)
                pregunta_reformulada = self.generator.generate(prompt_reformulacion).strip()
                pregunta_lower_reformulada = pregunta_reformulada.lower() # Convertimos la frase reformulada a minúsculas para analizar fácilmente palabras clavves
                # Actualiza la variable 'question' con la frase reformulada para que todo el código siguiente trabaje sobre esta nueva frase
                question = pregunta_reformulada  # pregunta_reformulada → Frase generada por Gemini, ya preparada para procesar
                # También actualiza 'pregunta_lower' para que las comprobaciones sean sobre la reformulación en minúsculas
                pregunta_lower = pregunta_lower_reformulada  
            except Exception as e:
                print(f"Error al reformular pregunta: {e}")

        # Detectar nombres válidos desde la fuente activa
        
        nombres_validos_original = obtener_lista_nombres_desde_calendar()
        nombres_validos = [n.lower() for n in nombres_validos_original]
        nombre_detectado = next((n for n in nombres_validos if re.search(rf'\b{re.escape(n)}\b', pregunta_lower)), None)

        # --- Detecta año en la pregunta (por ejemplo, "2024", "2025", etc)
        match_anio = re.search(r"(20\d{2})", pregunta_lower)
        anio = int(match_anio.group(1)) if match_anio else 2025  # 2025 por defecto
        semana_actual = date.today().isocalendar()[1]
        anio_actual = date.today().year
        semana = None

        if "esta semana" in pregunta_lower:
            semana = semana_actual
            anio = anio_actual
        elif "la semana que viene" in pregunta_lower or "semana que viene" in pregunta_lower:
            semana = semana_actual + 1
            anio = anio_actual

        # Detecta si se pregunta por hoy o mañana
        dia = None
        if "hoy" in pregunta_lower:
            dia = datetime.today().date()
        elif "mañana" in pregunta_lower:
            dia = (datetime.today() + timedelta(days=1)).date()
       
        # --- Detección tipo de evento:
        if any(pal in pregunta_lower for pal in ["reunion", "reuniones", "meeting", "cita"]):
            tipo_evento = "reuniones"
        elif any(pal in pregunta_lower for pal in ["festivo", "festivos", "fiesta", "fiestas"]):
            tipo_evento = "festivos"
        elif any(pal in pregunta_lower for pal in ["sprint", "sprints"]):
            tipo_evento = "sprints"
        elif any(pal in pregunta_lower for pal in ["entrega", "entregas", "deadline"]):
            tipo_evento = "entregas"
        else:
            tipo_evento = "vacaciones"

        # --- Si no hay nombre, pero se pregunta por reuniones/festivos, se asume que se refiere a = "todos"
        if not nombre_detectado and tipo_evento in ["reuniones", "festivos", "entregas", "sprints"]:
            nombre_detectado = "todos"

        try:
            #  --- Si el usuario quiere crear un evento y Google Calendar está activo, pasamos a crear el evento ---
            if es_intencion_crear:    
                # # Buscamos la fecha y la hora en la frase reformulada
                match_titulo = re.split(r"\s+a\s+las\s+", pregunta_lower_reformulada)
                titulo_limpio = match_titulo[0].strip().capitalize() if match_titulo else pregunta_reformulada
                # Buscamos la fecha y la hora en la reformulación, para asegurar máxima robustez
                match_fecha = re.search(r"(?:el\s)?(\d{1,2})\s+de\s+([a-záéíóú]+)", pregunta_lower_reformulada)
                match_hora = re.search(r"a\s+las\s+(\d{1,2})(?::(\d{2}))?", pregunta_lower_reformulada)
                
                 # Diccionario para pasar de nombre de mes a número 
                meses = {
                    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
                }
                # Solo seguimos si encontramos una fecha y una hora (o si es "hoy"/"mañana")
                if (match_fecha or "hoy" in pregunta_lower_reformulada or "mañana" in pregunta_lower_reformulada) and match_hora:
                    hora = int(match_hora.group(1))
                    minuto = int(match_hora.group(2)) if match_hora.group(2) else 0
                    if match_fecha:
                        dia_ = int(match_fecha.group(1))
                        mes_ = meses.get(match_fecha.group(2), None)
                        if not mes_:
                            return "Mes no reconocido para crear la reunión."
                        fecha_inicio = datetime(anio, mes_, dia_, hora, minuto)
                    elif "hoy" in pregunta_lower_reformulada:
                        fecha_inicio = datetime.today().replace(hour=hora, minute=minuto, second=0, microsecond=0)
                    elif "mañana" in pregunta_lower_reformulada:
                        fecha_inicio = (datetime.today() + timedelta(days=1)).replace(hour=hora, minute=minuto, second=0, microsecond=0)
                        
                    
                    # La reunión dura 1 hora por defecto    
                    fecha_fin = fecha_inicio + timedelta(hours=1)
                    # Llamamos a la función que esta en servoces/calendar_create.py crea el evento en Google Calendar
                    resultado = crear_evento_en_calendar(titulo_limpio, fecha_inicio, fecha_fin)
                    
                    return f"{resultado}"  # Ejemplo: "Evento creado correctamente"
                 # Si falta algún dato clave, avisamos al usuario
                return "Evento no creado: no he entendido bien la fecha o la hora para crear la reunión."

           
            elif nombre_detectado:
                resumen_dias = obtener_periodos_evento(
                    nombre_detectado, tipo_evento=tipo_evento, anio=anio
                )
                if tipo_evento == "entregas" and "siguiente" in pregunta_lower:
                    resumen_dias = sorted(resumen_dias, key=lambda x: x[0])
                    hoy = datetime.today().date()
                    proximas = [evento for evento in resumen_dias if (evento[0].date() if isinstance(evento[0], datetime) else evento[0]) > hoy]
                    resumen_dias = [proximas[0]] if proximas else []

                if semana:
                    resumen_dias = filtrar_por_semana(resumen_dias, anio, semana)
                    print(f"Aplicando filtro por semana: {semana}, año: {anio}")
                if dia:
                    resumen_dias = filtrar_por_dia(resumen_dias, dia)
                    print(f"{len(resumen_dias)} eventos recuperados antes de filtrar")

                match_mes = re.search(
                    r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)", pregunta_lower
                )
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
                    nombre_detectado,
                    resumen_dias,
                    self.generator,
                    tipo_evento=tipo_evento,
                    anio=anio,
                    mes=mes,
                    semana=semana,
                    dia=dia
                )
                return respuesta
            elif es_intencion_crear and not usar_google_calendar:
                return "La función de crear eventos solo está disponible si Google Calendar está activo."
            else:
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

        except Exception as e:
            return f"Error al consultar los días de vacaciones: {str(e)}"
