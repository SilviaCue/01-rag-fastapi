

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
    Redacta una respuesta clara y natural usando Gemini.

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
Contexto:
{contexto}

Instrucciones:
- Calcula el total de días laborables de vacaciones (lunes a viernes).
- Resume los periodos con fechas de inicio y fin exactas.
- Redacta la respuesta de forma clara, directa, amable y profesional.
- Evita repetir literalmente la lista. Resume los datos de forma natural.
- Limítate a los datos del contexto.

Pregunta:
¿Cuántos días de vacaciones ha tomado {nombre.title()} en 2025 y en qué fechas?
"""

    return generator.generate(prompt.strip())
