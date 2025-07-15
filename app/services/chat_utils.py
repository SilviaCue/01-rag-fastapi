from datetime import datetime, timedelta
import calendar

def contar_laborables(inicio: datetime.date, fin: datetime.date) -> int:
    dias_laborables = 0
    dia = inicio
    while dia <= fin:
        if dia.weekday() < 5:  # lunes a viernes
            dias_laborables += 1
        dia += timedelta(days=1)
    return dias_laborables

def filtrar_por_mes(resumen_dias, mes):
    resultado = []
    for evento in resumen_dias:
        inicio, fin = evento[:2]
        if inicio.month == mes or fin.month == mes:
            resultado.append(evento)
    return resultado

def responder_con_gemini(nombre: str, resumen_dias: list, generator, tipo_evento="vacaciones", anio=2025, mes=None):
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
    if mes:
        resumen_dias = sorted(filtrar_por_mes(resumen_dias, mes), key=lambda x: x[0]) 

    if not resumen_dias:
        mes_nombre = calendar.month_name[mes] if mes else f"el año {anio}"
        return f"No hay {tipo_evento} registrados para {nombre.title()} en {mes_nombre}."

    detalles = []
    total_laborables = 0

    for evento in resumen_dias:
        inicio, fin, duracion, *extra = evento

        if tipo_evento == "reuniones":
            titulo = extra[0] if len(extra) > 0 else "Sin título"
            hora_local = (inicio + timedelta(hours=2)).strftime('%H:%M')  # Ajuste de UTC a GMT+2
            detalles.append(f"- El {inicio.strftime('%d de %B de %Y')} a las {hora_local} ({titulo})")

            
            
        elif tipo_evento == "festivos":
            titulo = extra[0] if len(extra) > 0 else "Festivo"
            detalles.append(f"- {inicio.strftime('%d/%m/%Y')} ({titulo})")
        else:
            laborables = contar_laborables(inicio, fin)
            total_laborables += laborables
            detalles.append(f"- Del {inicio.strftime('%d/%m/%Y')} al {fin.strftime('%d/%m/%Y')} ({laborables} días laborables)")

    contexto = f"{nombre.title()} ha tenido {tipo_evento} en los siguientes periodos de {anio}:\n" + "\n".join(detalles)

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
- Utiliza un tono profesional, amable y natural.
- Limítate a la información del contexto.

Ejemplos de respuesta según tipo de evento:

Ejemplo para vacaciones:
"Silvia ha disfrutado de un total de 4 días laborables de vacaciones en 2025:
- Del 12 al 14 de junio (3 días laborables).
- El 15 de mayo (1 día laborable).
Actualmente no tiene más vacaciones registradas para este año."

Ejemplo para reuniones:
"En el mes de julio de 2025 se han registrado 2 reuniones:
- El 3 de julio a las 12:00 con IGEAR.
- El 15 de julio a las 13:00 con Pepito.
Estas reuniones suman un total de 2 reuniones este mes."

Ejemplo para festivos:
"En 2025, hay un total de 2 días festivos registrados:
- El 1 de mayo (viernes, Día del Trabajo).
- El 12 de octubre (lunes, Fiesta Nacional).
No hay más festivos registrados para este año."

Pregunta:
{pregunta}
"""

    return generator.generate(prompt.strip())
