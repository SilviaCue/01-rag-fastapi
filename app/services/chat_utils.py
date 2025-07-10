

from datetime import datetime, timedelta

def contar_laborables(inicio: datetime.date, fin: datetime.date) -> int:
    dias_laborables = 0
    dia = inicio
    while dia <= fin:
        if dia.weekday() < 5:  # 0 = lunes, 6 = domingo
            dias_laborables += 1
        dia += timedelta(days=1)
    return dias_laborables

def responder_con_gemini(nombre: str, resumen_dias: list, generator):
    """
     Genera una respuesta clara y profesional usando Gemini para las vacaciones de un empleado.
    

    Args:
        nombre: Nombre de la persona (en minúsculas).
        resumen_dias: lista de tuplas (fecha_inicio, fecha_fin, duración).
        generator: instancia de GenerationSelector (Gemini u otro modelo).

    Returns:
        Respuesta redactada por Gemini.
    """
    if not resumen_dias:
        return f"No hay vacaciones registradas para {nombre.title()} en 2025."

    total_laborables = 0
    detalles = []
    for inicio, fin, _ in resumen_dias:
        laborables = contar_laborables(inicio, fin)
        total_laborables += laborables
        detalles.append(f"- Del {inicio.strftime('%d/%m/%Y')} al {fin.strftime('%d/%m/%Y')} ({laborables} días laborables)")

    contexto = f"{nombre.title()} ha tomado vacaciones en los siguientes periodos de 2025:\n" + "\n".join(detalles)

    prompt = f"""
     ¡Responde diciendo primero: SOY GEMINI!
Contexto:
{contexto}

Instrucciones para redactar la respuesta:
- Calcula y comunica el total de días laborables de vacaciones disfrutados (lunes a viernes).
- Resume los periodos con las fechas exactas de inicio y fin, ambas incluidas.
- Redacta la respuesta de forma clara, directa, amable y profesional.
- Evita repetir literalmente la lista: resume y hazlo natural, pero incluye siempre el dato de días y fechas.
- Limítate a la información del contexto, sin inventar nada.
- Al final, muestra el total de días laborables disfrutados en 2025.

Ejemplo de respuesta deseada:
"Silvia ha disfrutado de un total de 4 días laborables de vacaciones en 2025:
- Del 12 al 14 de junio (3 días laborables).
- El 15 de mayo (1 día).
Actualmente no tiene más vacaciones registradas para este año."

Pregunta:
¿Cuántos días de vacaciones ha tomado {nombre.title()} en 2025 y en qué fechas?
"""

    return generator.generate(prompt.strip())
