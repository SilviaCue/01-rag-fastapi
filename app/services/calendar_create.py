import requests
from datetime import datetime

CALENDAR_POST_URL = "https://script.google.com/macros/s/AKfycbxTKuhVyHaWQAKtniDt8Tsq2IMCAjgqWgdwgveJTiePl1TS0kcaW08wupxOEnzQuz94/exec"

def crear_evento_en_calendar(titulo: str, fecha_inicio: datetime, fecha_fin: datetime) -> str:
    try:
        datos = {
            "titulo": titulo,
            "fechaInicio": fecha_inicio.isoformat(),  # "2025-08-13T15:00:00"
            "fechaFin": fecha_fin.isoformat()
        }

        response = requests.post(CALENDAR_POST_URL, json=datos)
        response.raise_for_status()
        return response.text

    except Exception as e:
        return f"Error al crear evento: {str(e)}"
