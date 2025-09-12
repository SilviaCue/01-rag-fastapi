# Importaciones librerías necesarias del sistema, fechas y módulos propios del proyecto
import os
import re
import glob  # AJUSTE MINIMO: para localizar los .txt generados de PDFs
from datetime import datetime, date, timedelta

# Función para unificar las fechas
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}
def extraer_filtros_fecha(texto: str, anio_defecto: int = 2025):
    texto_minusculas = texto.lower()
    fecha_hoy = date.today()
    filtros = {"anio": anio_defecto, "semana": None, "dia": None, "mes": None}

    # Año explícito (en este caso 2025)
    coincidencia_anio = re.search(r"(20\d{2})", texto_minusculas)
    if coincidencia_anio:
        filtros["anio"] = int(coincidencia_anio.group(1))

    # Semana
    if "esta semana" in texto_minusculas:
        filtros["semana"] = fecha_hoy.isocalendar()[1]
        filtros["anio"] = fecha_hoy.isocalendar()[0]
    elif "la semana que viene" in texto_minusculas or "semana que viene" in texto_minusculas:
        filtros["semana"] = fecha_hoy.isocalendar()[1] + 1
        filtros["anio"] = fecha_hoy.isocalendar()[0]

    # Día
    if "hoy" in texto_minusculas:
        filtros["dia"] = fecha_hoy
    elif "mañana" in texto_minusculas:
        filtros["dia"] = fecha_hoy + timedelta(days=1)

    # Mes por nombre
    coincidencia_mes = re.search(
        r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)",
        texto_minusculas
    )
    if coincidencia_mes:
        filtros["mes"] = MESES[coincidencia_mes.group(1)]

    return filtros


# Importaciones de los módulos del proyecto
from app.services.retriever import Retriever  # Encargado de buscar fragmentos relevantes en los documentos
from app.config import settings  # Configuración general
from app.services.generation_selector import GenerationSelector  # Decide qué modelo usar para generar texto
# Funciones para leer nombres y eventos del calendarios
from app.services.vacaciones_googlecalendar import (
    obtener_lista_nombres_desde_calendar,  # función para sacar los nombres
    obtener_periodos_evento,  # función para sacar los eventos de calendario
    filtrar_por_semana,  # función para quedarte solo con eventos de cierta semana
    filtrar_por_dia  # función para quedarte solo con eventos de un día
)
# Función para generar respuestas usando IA (Gemini)
from app.services.chat_utils import responder_con_gemini

# Función que crea eventos en Google Calendar
from app.services.calendar_create import crear_evento_en_calendar

# >>> IMPORTACIÓN NUEVA (único cambio en imports) <<<
from app.services.file_parser import FileParser


# Clase principal del sistema de chat
class ChatRAG:
    def __init__(self):
        self.retriever = Retriever()  # Para buscar fragmentos de texto relevantes
        self.generator = GenerationSelector(settings.GENERATION_MODEL)  # Para generar respuestas con IA
        self.upload_path = "storage/docs_raw"  # Carpeta donde están los documentos subidos
        self.pending_event = None  # dict {titulo, titulo_sugerido, fecha_inicio, fecha_fin, invitados_validos, invitados_invalidos}

    def chat(self, question: str):
        # AJUSTE 1/2: conservar el texto original antes de reformular (lo usaremos para extraer emails)
        question_original = question

        pregunta_lower = question.lower()
        pregunta_lower_reformulada = pregunta_lower  # Se usará luego

        # Confirmaciones ampliadas (sinónimos naturales)
        confirma_alias = any(x in pregunta_lower for x in [
            "confirmo", "confirmar", "ok, confirma", "vale confirma", "te confirmo",
            "adelante", "crear", "crea", "ok", "vale", "sí", "si"
        ])
        cancela = any(x in pregunta_lower for x in [
            "cancelar", "cancela", "no confirmo", "no cancela", "no cancelar", "no cancela", "no", "no quiero", "no gracias"
        ])

        # =================== BLOQUE PENDIENTE (2 PASOS: título -> confirmar) ===================
        if self.pending_event:
            # 1) TÍTULO: aceptar comando y entrada libre
            # comando explícito
            m_titulo_cmd = re.search(r'^\s*t[ií]tulo\s*:\s*(.+)$', question, flags=re.IGNORECASE)
            if m_titulo_cmd:
                titulo_nuevo = m_titulo_cmd.group(1).strip().strip(" .,-:;()[]{}'\"")
                if titulo_nuevo:
                    self.pending_event["titulo"] = titulo_nuevo
                    # tras fijar título: si hay invitados → pedir confirmación final (Paso 2)
                    inicio_fmt = self.pending_event["fecha_inicio"].strftime("%d/%m %H:%M")
                    fin_fmt = self.pending_event["fecha_fin"].strftime("%d/%m %H:%M")
                    if self.pending_event.get("invitados_validos"):
                        invitados_txt = ", ".join(self.pending_event["invitados_validos"])
                        return (f"¿Lo creo e invito ya?\n"
                                f"Responde: ok / vale / sí / confirmo / te confirmo / crear / crea")
                    # si no hay invitados → confirmar creación directa
                    return (f"¿Lo creo ya?\n"
                            f"Responde: ok / vale / sí / confirmo / te confirmo / crear / creA")
                else:
                    return "El título no puede estar vacío. Escribe: título: Nombre exacto"

            # entrada libre de título (si falta)
            if not self.pending_event.get("titulo"):
                # cualquier texto distinto de ok/vale/confirmo/cancelar se toma como título
                if not cancela and not confirma_alias and not re.fullmatch(r'\s*(ok|vale)\s*', pregunta_lower, flags=re.IGNORECASE):
                    posible_titulo = question.strip().strip(" .,-:;()[]{}'\"")
                    if posible_titulo:
                        self.pending_event["titulo"] = posible_titulo
                        if self.pending_event.get("invitados_validos"):
                            return (f"¿Lo creo e invito ya?\n"
                                    f"Por favor confirma que quieres crear el evento.")
                        return (f"¿Lo creo ya?\n"
                                f"¿Esta todo correcto?")
                # pedir título claro (Paso 1)
                sugerido = self.pending_event.get("titulo_sugerido")
                inicio_fmt = self.pending_event["fecha_inicio"].strftime("%d/%m %H:%M")
                fin_fmt = self.pending_event["fecha_fin"].strftime("%d/%m %H:%M")
                invitados_txt = ", ".join(self.pending_event.get("invitados_validos", [])) if self.pending_event.get("invitados_validos") else "(ninguno)"
                if sugerido:
                    return (f"Propuesta de evento:\n"
                            f"Inicio {inicio_fmt} – Fin {fin_fmt}\n"
                            f"Invitados: {invitados_txt}\n\n"
                            f"¿Confirma o escribe de nuevo el título de la reunión? (ej.: {sugerido})\n"
                            f"Escribe: título: {sugerido}")
                return (f"Propuesta de evento:\n"
                        f"Inicio {inicio_fmt} – Fin {fin_fmt}\n"
                        f"Invitados: {invitados_txt}\n\n"
                        f"Confirma o escribe de nuevo el título de la reunión?\n"
                        f"Escribe: título: …")

            # 2) (Opcional) Ajuste de invitados: mantenemos funcionalidad, no la anunciamos
            if self.pending_event.get("invitados_validos"):
                m_add = re.search(r'^\s*añade\s*:\s*(.+)$', question, flags=re.IGNORECASE)
                if m_add:
                    nuevos = [e.strip().lower() for e in re.split(r'[,\s;]+', m_add.group(1)) if e.strip()]
                    for e in nuevos:
                        if re.match(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", e):
                            if e not in self.pending_event["invitados_validos"]:
                                self.pending_event["invitados_validos"].append(e)
                        else:
                            self.pending_event.setdefault("invitados_invalidos", []).append(e)
                    listado = ", ".join(self.pending_event["invitados_validos"]) if self.pending_event["invitados_validos"] else "(ninguno)"
                    return (f"Invitados actualizados: {listado}.\n"
                            f"¿Lo creo e invito ya?\n"
                            f"Responde: ok / vale / sí / confirmo / te confirmo / crear / crea")

                m_del = re.search(r'^\s*quita\s*:\s*(.+)$', question, flags=re.IGNORECASE)
                if m_del:
                    quitar = {e.strip().lower() for e in re.split(r'[,\s;]+', m_del.group(1)) if e.strip()}
                    self.pending_event["invitados_validos"] = [e for e in self.pending_event["invitados_validos"] if e not in quitar]
                    listado = ", ".join(self.pending_event["invitados_validos"]) if self.pending_event["invitados_validos"] else "(ninguno)"
                    return (f"Invitados actualizados: {listado}.\n"
                            f"¿Lo creo e invito ya?\n"
                            f"Responde: ok / vale / sí / confirmo / te confirmo / crear / crea")

            # CONFIRMAR (directo): crear evento ya (alias naturales)
            if confirma_alias:
                pe = self.pending_event
                if not pe.get("titulo"):
                    sugerido = pe.get("titulo_sugerido", "Reunión")
                    return f"Falta el título. Escribe: título: {sugerido}"
                self.pending_event = None  # limpiar estado
                invitados_finales = list(dict.fromkeys(list(settings.ALERT_EMAILS) + pe.get("invitados_validos", [])))
                resultado = crear_evento_en_calendar(
                    pe["titulo"], pe["fecha_inicio"], pe["fecha_fin"],
                    guests=invitados_finales if invitados_finales else None
                )
                aviso_invalidos = ""
                if pe.get("invitados_invalidos"):
                    aviso_invalidos = f"\nAviso: ignoré por formato inválido: {', '.join(pe['invitados_invalidos'])}."
                invitados_info = f"\nInvitaciones enviadas a: {', '.join(invitados_finales)}." if invitados_finales else ""
                return f"{resultado}{invitados_info}{aviso_invalidos}"

            if cancela:
                self.pending_event = None
                return "He cancelado la propuesta de creación del evento."

            # Recordatorio genérico
            return "Tengo una propuesta pendiente. Escribe el título con `título: …` y luego responde ok/vale/sí/confirmo/te confirmo/crear/crea."

        # --- Detección de intención de creación de evento (antes de reformular con Gemini)
        es_intencion_crear = any(
            pal in pregunta_lower for pal in [
                "crear", "añadir", "añade", "crea", "quiero", "me gustaria", "pon", "poner", "agenda", "agendar", "programa", "programar"
            ]
        )
        # Guarda la pregunta original tal cual
        pregunta_reformulada = question
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
                pregunta_reformulada = self.generator.generate(prompt_reformulacion).strip()
                pregunta_lower_reformulada = pregunta_reformulada.lower()
                question = pregunta_reformulada
                pregunta_lower = pregunta_lower_reformulada
            except Exception as e:
                print(f"Error al reformular pregunta: {e}")

        # Detectar nombres válidos desde la fuente activa
        nombres_validos_original = obtener_lista_nombres_desde_calendar()
        nombres_validos = [n.lower() for n in nombres_validos_original]
        nombre_detectado = next((n for n in nombres_validos if re.search(rf'\b{re.escape(n)}\b', pregunta_lower)), None)

        # Fechas
        filtros = extraer_filtros_fecha(pregunta_lower)
        anio = filtros["anio"]
        semana = filtros["semana"]
        dia = filtros["dia"]
        mes = filtros["mes"]

        # Tipo de evento
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

        if not nombre_detectado and tipo_evento in ["reuniones", "festivos", "entregas", "sprints"]:
            nombre_detectado = "todos"

        try:
            #  --- Creación de evento ---
            if es_intencion_crear:
                # Título sugerido (conservar mayúsculas del texto reformulado)
                titulo_base_text = re.split(r"\s+a\s+las\s+\d{1,2}(?::\d{2})?", pregunta_reformulada, maxsplit=1, flags=re.IGNORECASE)[0]
                titulo_sugerido = re.sub(r"\b(hoy|mañana)\b", "", titulo_base_text, flags=re.IGNORECASE)
                titulo_sugerido = re.sub(
                    r"\bel\s+\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b",
                    "",
                    titulo_sugerido,
                    flags=re.IGNORECASE
                )
                titulo_sugerido = titulo_sugerido.strip(" .,-:;()[]{}'\"")
                titulo_sugerido = re.sub(r"\s{2,}", " ", titulo_sugerido).strip() or "Reunión"

                # Fecha/hora (desde la versión en minúsculas)
                match_fecha = re.search(r"(?:el\s)?(\d{1,2})\s+de\s+([a-záéíóú]+)", pregunta_lower)
                match_hora = re.search(r"a\s+las\s+(\d{1,2})(?::(\d{2}))?", pregunta_lower)
                meses_para_creacion = MESES
                if (match_fecha or "hoy" in pregunta_lower or "mañana" in pregunta_lower) and match_hora:
                    hora = int(match_hora.group(1))
                    minuto = int(match_hora.group(2)) if match_hora.group(2) else 0
                    if match_fecha:
                        dia_ = int(match_fecha.group(1))
                        mes_ = meses_para_creacion.get(match_fecha.group(2), None)
                        if not mes_:
                            return "Mes no reconocido para crear la reunión."
                        fecha_inicio = datetime(anio, mes_, dia_, hora, minuto)
                    elif "hoy" in pregunta_lower:
                        fecha_inicio = datetime.today().replace(hour=hora, minute=minuto, second=0, microsecond=0)
                    elif "mañana" in pregunta_lower:
                        fecha_inicio = (datetime.today() + timedelta(days=1)).replace(hour=hora, minute=minuto, second=0, microsecond=0)
                    fecha_fin = fecha_inicio + timedelta(hours=1)

                    # Emails
                    texto_busqueda_emails = (question_original or "") + " " + (pregunta_lower or "")
                    texto_busqueda_emails = texto_busqueda_emails.replace(" y ", ",").replace(";", ",")
                    posibles_emails = re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", texto_busqueda_emails)
                    normalizados, vistos = [], set()
                    for e in posibles_emails:
                        e2 = e.strip().lower()
                        if e2 and e2 not in vistos:
                            normalizados.append(e2)
                            vistos.add(e2)
                    invitados_validos, invitados_invalidos = [], []
                    for e in normalizados:
                        try:
                            dominio = e.split("@", 1)[1]
                            (invitados_validos if "." in dominio else invitados_invalidos).append(e)
                        except Exception:
                            invitados_invalidos.append(e)

                    # Guardar propuesta (título pendiente) — 2 pasos
                    self.pending_event = {
                        "titulo": None,
                        "titulo_sugerido": titulo_sugerido,
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "invitados_validos": invitados_validos,
                        "invitados_invalidos": invitados_invalidos,
                    }

                    inicio_fmt = fecha_inicio.strftime("%d/%m %H:%M")
                    fin_fmt = fecha_fin.strftime("%d/%m %H:%M")
                    invitados_txt = ", ".join(invitados_validos) if invitados_validos else "(ninguno)"

                    resumen = [
                        "Propuesta de evento:",
                        f"Inicio {inicio_fmt} – Fin {fin_fmt}",
                        f"Invitados: {invitados_txt}",
                        "",
                        f"Confirma o escribe de nuevo el título de la reunión. (ej.: {titulo_sugerido})",
                        f"Escribe: título: {titulo_sugerido}",
                    ]
                    return "\n".join(resumen)

                return "Evento no creado: no he entendido bien la fecha o la hora para crear la reunión."

            # --- Consulta de eventos (no creación) ---
            elif nombre_detectado:
                resumen_dias = obtener_periodos_evento(nombre_detectado, tipo_evento=tipo_evento, anio=anio)
                if tipo_evento == "entregas" and "siguiente" in pregunta_lower:
                    resumen_dias = sorted(resumen_dias, key=lambda x: x[0])
                    hoy = datetime.today().date()
                    proximas = [evento for evento in resumen_dias if (evento[0].date() if isinstance(evento[0], datetime) else evento[0]) > hoy]
                    resumen_dias = [proximas[0]] if proximas else []
                if semana:
                    resumen_dias = filtrar_por_semana(resumen_dias, anio, semana)
                if dia:
                    resumen_dias = filtrar_por_dia(resumen_dias, dia)
                if not resumen_dias:
                    if semana:
                        return f"No hay {tipo_evento} programadas para la semana {semana} del año {anio}."
                    elif dia:
                        return f"No hay {tipo_evento} programadas para el día {dia.strftime('%d/%m/%Y')}."
                    elif mes:
                        mes_nombre = next((nombre for nombre, numero in MESES.items() if numero == mes), None)
                        return f"No hay {tipo_evento} programadas para el mes de {mes_nombre} del año {anio}."
                    else:
                        return f"No hay {tipo_evento} registrados para {nombre_detectado.capitalize()} en el año {anio}."
                respuesta = responder_con_gemini(
                    nombre_detectado, resumen_dias, self.generator,
                    tipo_evento=tipo_evento, anio=anio, mes=mes, semana=semana, dia=dia
                )
                return respuesta

            else:
                # === AJUSTE MINIMO: respuesta desde PDFs si hay ===
                pdf_txts = [p for p in glob.glob(os.path.join("storage", "docs_chunks", "*.txt")) if os.path.isfile(p)]

                # >>> BLOQUE NUEVO: AUTOPROCESAR PDFs -> TXT si no hay ninguno <<<
                if not pdf_txts:
                    try:
                        parser = FileParser(self.upload_path)
                        for file in os.listdir(self.upload_path):
                            if file.lower().endswith(".pdf"):
                                print(f"[AutoProcesar] Generando TXT con Gemini: {file}")
                                parser.parse_document(file)
                        # recargar lista de txts tras procesar
                        pdf_txts = [p for p in glob.glob(os.path.join("storage", "docs_chunks", "*.txt")) if os.path.isfile(p)]
                    except Exception as e:
                        print(f"[AutoProcesar] Error al procesar PDFs: {e}")

                if pdf_txts:
                    try:
                        textos_pdf = []
                        for p in pdf_txts:
                            with open(p, "r", encoding="utf-8") as f:
                                textos_pdf.append(f.read())
                        contexto_pdf = "\n".join(textos_pdf)[:24000]
                        prompt_pdf = f"""
Eres un asistente experto en interpretar instrucciones de documentos de la empresa Idearium extraídas de PDFs (capturas y pasos).
Responde de forma clara, ordenada y profesional. NO inventes información que no aparezca en el texto.

CONTEXT (de PDFs):
\"\"\"{contexto_pdf}\"\"\"


PREGUNTA DEL USUARIO:
\"{question}\"
"""
                        respuesta_pdf = self.generator.generate(prompt_pdf)
                        if respuesta_pdf and respuesta_pdf.strip():
                            return respuesta_pdf
                    except Exception as e:
                        print(f"AVISO: fallo en respuesta desde PDFs: {e}")

                # (Resto del flujo original con retriever)
                resultados = self.retriever.retrieve(question, top_k=12)
                contexto = "\n".join([res["text"] for res in resultados])[:14000]
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
