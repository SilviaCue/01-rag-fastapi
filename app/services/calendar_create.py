import requests
from datetime import datetime
from typing import Optional, List

CALENDAR_POST_URL = "https://script.google.com/macros/s/AKfycbzwM8osD7jWBqr3Dfsx_il59rEie4BE-oQ5usPDG0iNugiDEAbs50JKFsUKrqNiH8dQmg/exec"

def crear_evento_en_calendar(
    titulo: str,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    guests: Optional[List[str]] = None,   # ahora soporta invitados
) -> str:
    try:
        datos = {
            "titulo": titulo,
            "fechaInicio": fecha_inicio.isoformat(),
            "fechaFin": fecha_fin.isoformat(),
        }
        if guests:
            datos["guests"] = guests  # se envía en el JSON

        response = requests.post(CALENDAR_POST_URL, json=datos, timeout=20)
        response.raise_for_status()
        return response.text

    except Exception as e:
        return f"Error al crear evento: {str(e)}"
    
