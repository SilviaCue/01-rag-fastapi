from datetime import datetime, timedelta
import calendar

# Contar días laborables entre dos fechas, excluyendo fines de semana
def contar_laborables(inicio: datetime.date, fin: datetime.date) -> int:
    dias_laborables = 0
    dia = inicio
    while dia <= fin:
        if dia.weekday() < 5:  # lunes a viernes
            dias_laborables += 1
        dia += timedelta(days=1)
    return dias_laborables

# Filtrar eventos que ocurren en un mes específico
def filtrar_por_mes(resumen_dias, mes):
    resultado = []
    for evento in resumen_dias:
        inicio, fin = evento[:2]
        if inicio.month == mes or fin.month == mes:
            resultado.append(evento)
    return resultado

# Función principal para generar respuestas usando IA (Gemini/OpenAI)
def responder_con_gemini(nombre: str, resumen_dias: list, generator, tipo_evento="vacaciones", anio=2025, mes=None, semana=None, dia=None):
    """
    Genera una respuesta clara y profesional usando IA (Gemini/OpenAI) para eventos.

    Args:
        nombre (str): nombre de la persona (en minúsculas).
        resumen_dias (list): lista de tuplas (inicio, fin, duracion, [titulo], [descripcion]).
        generator: instancia de GenerationSelector (Gemini u OpenAI).
        tipo_evento (str): tipo de evento ('vacaciones', 'reuniones', etc).
        anio (int): Año de consulta.
        mes (int): Mes específico (opcional).

    Returns:
        Respuesta redactada por la IA.
    """
    # Filtrar por mes si se especifica
    if mes:
        resumen_dias = sorted(filtrar_por_mes(resumen_dias, mes), key=lambda x: x[0])
    # Filtrar por semana o día si se especifica
    if not resumen_dias:
        if semana:
            detalles = [f"No hay {tipo_evento} programadas para la semana {semana} del año {anio}."]
        elif dia:
            detalles = [f"No hay {tipo_evento} programadas para el día {dia.strftime('%d/%m/%Y')}."]
        elif mes:
            mes_nombre = calendar.month_name[mes] if isinstance(mes, int) and 1 <= mes <= 12 else f"mes {mes}"
            detalles = [f"No hay {tipo_evento} programadas para el mes de {mes_nombre} del año {anio}."]
        else:
            detalles = [f"No hay {tipo_evento} registrados para {nombre.capitalize()} en el año {anio}."]
        # Generar prompt para respuesta negativa
        contexto = "\n".join(detalles)
        # Crear la pregunta
        pregunta = f"¿Qué {tipo_evento} ha tenido {nombre.title()} en {anio} y en qué fechas?"
        prompt = f"""
Contexto:
{contexto}

Instrucciones para redactar la respuesta:
- Responde claramente si no hay eventos.
- Mantén un tono profesional y claro.

Pregunta:
{pregunta}
"""
        return generator.generate(prompt.strip())
    #detallar eventos
    detalles = []
    # Contador de días laborables para vacaciones
    total_laborables = 0
        # Procesar cada evento
    for evento in resumen_dias:
        inicio, fin, duracion, *extra = evento
        #tipo de evento específico
        if tipo_evento == "reuniones":
            titulo = extra[0] if len(extra) > 0 else "Sin título"
            hora_local = (inicio + timedelta(hours=2)).strftime('%H:%M')  # Ajuste de UTC a GMT+2
            detalles.append(f"- El {inicio.strftime('%d de %B de %Y')} a las {hora_local} ({titulo})")

        elif tipo_evento == "entregas":
            titulo = extra[0] if len(extra) > 0 else "Entrega"
            fecha_entrega = inicio.strftime('%d de %B de %Y')
            if len(resumen_dias) == 1:
                detalles.append(f"La próxima entrega es el {fecha_entrega} ({titulo}).")
            else:
                detalles.append(f"- {fecha_entrega} ({titulo})")
        
        elif tipo_evento == "sprints":
            titulo = extra[0] if len(extra) > 0 else "Sprint"
            fecha_sprint = inicio.strftime('%d de %B de %Y')
            if len(resumen_dias) == 1:
                detalles.append(f"El próximo sprint es el {fecha_sprint} ({titulo}).")
            else:
                detalles.append(f"- {fecha_sprint} ({titulo})")


        elif tipo_evento == "festivos":
            titulo = extra[0] if len(extra) > 0 else "Festivo"
            detalles.append(f"- {inicio.strftime('%d/%m/%Y')} ({titulo})")
        else:
            laborables = contar_laborables(inicio, fin)
            total_laborables += laborables
            detalles.append(f"- Del {inicio.strftime('%d/%m/%Y')} al {fin.strftime('%d/%m/%Y')} ({laborables} días laborables)")
        # Resumen total para vacaciones
    contexto = f"{nombre.title()} ha tenido {tipo_evento} en los siguientes periodos de {anio}:\n" + "\n".join(detalles)
        # Añadir total de días laborables si es vacaciones
    if mes:
        mes_nombre = calendar.month_name[mes]
        pregunta = f"¿Qué {tipo_evento} ha tenido {nombre.title()} en {mes_nombre} de {anio} y en qué fechas?"
    else:
        pregunta = f"¿Qué {tipo_evento} ha tenido {nombre.title()} en {anio} y en qué fechas?"

    prompt = f"""
Contexto:
{contexto}

Instrucciones para redactar la respuesta:
- Si son vacaciones, indica el total de días laborables y resume los periodos.
- Si se trata de reuniones, incluye la fecha, hora y título si está disponible.
- Si se trata de festivos, incluye fechas y nombres si existen.
- Mantén un tono profesional, amable y claro, orientado a usuarios que buscan información precisa.
- Limítate a la información del contexto.

Ejemplos de respuesta según tipo de evento:

Ejemplo para vacaciones:
"Silvia ha disfrutado de un total de 4 días laborables de vacaciones en 2025:
- Del 12 al 14 de junio (3 días laborables).
- El 15 de mayo (1 día laborable).
Actualmente no tiene más vacaciones registradas para este año."

Ejemplo para reuniones:
"En julio de 2025 se han registrado las siguientes reuniones:
- 3 de julio a las 12:00 con IGEAR.
- 15 de julio a las 13:00 con Pepito.
Reuniones pendientes:
- Hoy a las 11:00 con el Gobierno de Aragón.
- 20 de julio a las 10:00 con el Gobierno de Aragón.
Importante: Si no hay reuniones, responde no hay ninguna reunión programada"

Ejemplo para festivos:
"En 2025 hay registrados los siguientes festivos:
- 1 de mayo (viernes, Día del Trabajo).
- 12 de octubre (lunes, Fiesta Nacional).
No se han identificado más festivos para este año."

Ejemplo para entregas:
"En 2025 hay registradas las siguientes entregas:
- 25 de julio de 2025 (Entrega proyecto).
- 8 de octubre de 2025 (Informe trimestral).
Actualmente, no hay más entregas programadas para este año."

Ejemplo para sprints:
"En 2025 se han registrado los siguientes sprints:
- 12 de junio de 2025 (Sprint 2: Preparación Cartografía).
- 15 de julio de 2025 (Sprint 3: Validación Datos).
Actualmente no hay más sprints programados para este año."

Si solo hay una entrega futura:
"La próxima entrega es el 25 de julio de 2025 (Sprint 3)."

Pregunta:
{pregunta}
"""
# Generar la respuesta usando el generador de IA
    return generator.generate(prompt.strip())
