# Importaciones librerías necesarias del sistema, fechas y módulos propios del proyecto
import os
import re
from datetime import datetime, date, timedelta


# Función para unificar las fechas 

MESES = {
    "enero" :1,  "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    
}
def extraer_filtros_fecha(texto: str, anio_defecto:int =2025):
    texto_minusculas = texto.lower()
    fecha_hoy =date.today()
    filtros ={"anio":anio_defecto, "semana": None, "dia": None, "mes": None}
    
    # Año explicito ( en este caso 2025)
    coincidencia_anio = re.search(r"(20\d{2})", texto_minusculas)
    if coincidencia_anio:
        filtros["anio"] = int(coincidencia_anio.group(1))
        
    #Semana
    if"esta semana" in texto_minusculas:
        filtros["semana"] = fecha_hoy.isocalendar()[1]
        filtros["anio"] = fecha_hoy.isocalendar()[0]
    elif"la semana que viene" in texto_minusculas or "semana que viene" in texto_minusculas:
        filtros["semana"] = fecha_hoy.isocalendar()[1] + 1
        filtros["anio"] = fecha_hoy.isocalendar()[0]
        
    #Día
    if "hoy" in texto_minusculas:
        filtros["dia"] = fecha_hoy
    elif "mañana" in texto_minusculas:
        filtros ["dia"] = fecha_hoy + timedelta(days=1)
    
    #Mes por nombre
    coincidencia_mes =re.search(
         r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)",
        texto_minusculas
    )
    if coincidencia_mes:
        filtros["mes"] = MESES[coincidencia_mes.group(1)]
        
    return filtros
        
        
        

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
    

      # llamada centralizadapara las fechas
        filtros = extraer_filtros_fecha(pregunta_lower)
        anio = filtros["anio"]
        semana = filtros["semana"]
        dia = filtros["dia"]
        mes = filtros ["mes"]
       
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
                 # Buscamos el título del evento separando antes de "a las" por si hay hora
                match_titulo = re.split(r"\s+a\s+las\s+", pregunta_lower_reformulada)
                 # Obtenemos el título limpio, capitalizado
                titulo_limpio = match_titulo[0].strip().capitalize() if match_titulo else pregunta_reformulada
                 # Extraemos la fecha (día y mes) 
                match_fecha = re.search(r"(?:el\s)?(\d{1,2})\s+de\s+([a-záéíóú]+)", pregunta_lower_reformulada)
                  # Extraemos la hora (y minutos opcionales) 
                match_hora = re.search(r"a\s+las\s+(\d{1,2})(?::(\d{2}))?", pregunta_lower_reformulada)
                
                 # Diccionario para pasar de nombre de mes a número 
                meses_para_creacion = MESES
                # Solo seguimos si encontramos una fecha y una hora (o si es "hoy"/"mañana")
                if (match_fecha or "hoy" in pregunta_lower_reformulada or "mañana" in pregunta_lower_reformulada) and match_hora:
                       # Convertimos hora y minuto a enteros
                    hora = int(match_hora.group(1))
                    minuto = int(match_hora.group(2)) if match_hora.group(2) else 0
            
                    if match_fecha:
                        # Si hay fecha, extraemos día y mes
                        dia_ = int(match_fecha.group(1))
                        mes_ = meses_para_creacion.get(match_fecha.group(2), None) 
                        if not mes_:
                              # Si el mes no se reconoce, avisamos
                            return "Mes no reconocido para crear la reunión."
                         # Creamos objeto datetime para el inicio del evento
                        fecha_inicio = datetime(anio, mes_, dia_, hora, minuto)
                    elif "hoy" in pregunta_lower_reformulada:
                         # Si es hoy, usamos la fecha actual con hora/minuto
                        fecha_inicio = datetime.today().replace(hour=hora, minute=minuto, second=0, microsecond=0)
                    elif "mañana" in pregunta_lower_reformulada:
                        # Si es mañana, usamos la fecha de mañana con hora/minuto
                        fecha_inicio = (datetime.today() + timedelta(days=1)).replace(hour=hora, minute=minuto, second=0, microsecond=0)
                        
                    
                    # La reunión dura 1 hora por defecto    
                    fecha_fin = fecha_inicio + timedelta(hours=1)
                    
                    print("DEBUG EVENTO:", titulo_limpio, fecha_inicio, fecha_fin, settings.ALERT_EMAILS)
                    # Llamamos a la función que esta en servoces/calendar_create.py crea el evento en Google Calendar
                    resultado = crear_evento_en_calendar(titulo_limpio, fecha_inicio,fecha_fin, guests=settings.ALERT_EMAILS )
                    
                    return f"{resultado}"  # Ejemplo: "Evento creado correctamente"
                 # Si falta algún dato clave, avisamos al usuario
                return "Evento no creado: no he entendido bien la fecha o la hora para crear la reunión."

             # --- Si se detecta un nombre y no se está en modo creación de evento, s
            elif nombre_detectado:
                # Recuperamos los eventos del nombre detectado, tipo y año
                resumen_dias = obtener_periodos_evento(
                    nombre_detectado, tipo_evento=tipo_evento, anio=anio
                )
                # Si pidió la siguiente entrega, filtramos para mostrar sólo la próxima
                if tipo_evento == "entregas" and "siguiente" in pregunta_lower:
                    resumen_dias = sorted(resumen_dias, key=lambda x: x[0])
                    hoy = datetime.today().date()
                    proximas = [evento for evento in resumen_dias if (evento[0].date() if isinstance(evento[0], datetime) else evento[0]) > hoy]
                    resumen_dias = [proximas[0]] if proximas else []
                  # Filtramos por semana si está especificada
                if semana:
                    resumen_dias = filtrar_por_semana(resumen_dias, anio, semana)
                    print(f"Aplicando filtro por semana: {semana}, año: {anio}")
                     # Filtramos por día si está especificado
                if dia:
                    resumen_dias = filtrar_por_dia(resumen_dias, dia)
                    print(f"{len(resumen_dias)} eventos recuperados antes de filtrar")
        # Si no hay eventos tras el filtrado, informamos al usuario según el filtro aplicado
                if not resumen_dias:
                    if semana:
                        return f"No hay {tipo_evento} programadas para la semana {semana} del año {anio}."
                    elif dia:
                        return f"No hay {tipo_evento} programadas para el día {dia.strftime('%d/%m/%Y')}."
                    elif mes:
                        mes_nombre = None
                         # Buscamos el nombre del mes por el número
                        for nombre_mes in MESES.items():
                            if numero_mes ==mes:
                                mes_nombre = nombre_mes
                                break
                        return f"No hay {tipo_evento} programadas para el mes de {mes_nombre} del año {anio}."
                    else:
                        return f"No hay {tipo_evento} registrados para {nombre_detectado.capitalize()} en el año {anio}."
                # Si hay eventos, los pasamos a la función de respuesta con Gemin# Si hay eventos, generamos la respuesta usando Gemini
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
            
             # Si se quiso crear evento pero la función no está disponible, informamos al usuario
            elif es_intencion_crear and not settings.USAR_GOOGLE_CALENDAR:
                return "La función de crear eventos solo está disponible si Google Calendar está activo."
            else:
                # Si la pregunta no es sobre vacaciones, reuniones, etc., se usa el sistema RAG normal para buscar en la documentación
                resultados = self.retriever.retrieve(question, top_k=12)
                # Se junta el texto de los resultados en un solo string para usar como contexto. Se limita a 4000 caracteres por seguridad.
                contexto = "\n".join([res["text"] for res in resultados])[:4000]
                
                # Este es el prompt (instrucciones) que se le da a la IA para que genere una respuesta amable y profesional, usando solo la información del contexto
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
- Si tienes alguna duda, no dudes en contactar con RRHH.


Si necesitas más información, consulta el Manual de Bienvenida o contacta con RRHH.

Un saludo cordial,
El equipo de Idearium

"""
                try:
                     # Le pedimos a la IA que genere la respuesta usando el prompt y el contexto
                    respuesta = self.generator.generate(prompt)
                except Exception as e:
                                        # Si ocurre un error con la IA, devolvemos el error como respuesta
                    respuesta = f"Error al generar respuesta: {str(e)}"
                    
                # Si el usuario ha pedido descargar un documento (por ejemplo PDF), añadimos el enlace de descarga al final de la respuesta
                if any(x in pregunta_lower for x in ["descargar", "pdf", "documento"]):
                    documentos_utilizados = {res["document_id"] for res in resultados}
                    for doc in documentos_utilizados:
                        nombre_archivo = os.path.basename(doc)
                        # Si el nombre del archivo no termina en .pdf o .docx, lo añadimos
                        for ext in [".pdf", ".docx"]:
                            if not nombre_archivo.endswith(ext):
                                archivo_con_ext = f"{nombre_archivo}{ext}"
                            else:
                                archivo_con_ext = nombre_archivo

                            ruta_completa = os.path.join(self.upload_path, archivo_con_ext)
                            # Si el archivo existe en la carpeta, creamos el enlace de descarga
                            if os.path.isfile(ruta_completa):
                                url = f"http://127.0.0.1:8000/download/{archivo_con_ext}"
                                respuesta += f"\n\nPuedes descargar el documento '{archivo_con_ext}' aquí: {url}"
                                break
                 # Devolvemos la respuesta final al usuario
                return respuesta
         # Si ocurre cualquier error en el proceso (por ejemplo, al consultar días de vacaciones), lo devolvemos al usuario
        except Exception as e:
            return f"Error al consultar los días de vacaciones: {str(e)}"
