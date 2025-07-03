from datetime import datetime

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

    bloques = []
    total = 0
    for inicio, fin, dias in resumen_dias:
        total += dias
        bloques.append(f"- Del {inicio.strftime('%d/%m/%Y')} al {fin.strftime('%d/%m/%Y')} ({dias} días)")

    contexto = f"{nombre.title()} ha tomado vacaciones en los siguientes periodos de 2025:\n" + "\n".join(bloques)

    prompt = f"""
Eres el asistente de RRHH de Idearium. A continuación tienes los periodos de vacaciones registrados para {nombre.title()} en 2025:

{contexto}

Tu tarea es:
- Calcular el total de días de vacaciones.
- Responder a la pregunta "¿Cuántos días de vacaciones ha tomado {nombre.title()} en 2025 y cuándo?".
- Redactar la respuesta de forma clara, natural, profesional y amable.
- No repitas la lista completa. Haz un buen resumen.

Importante: Limítate a la información del contexto.
"""

    return generator.generate(prompt.strip())
