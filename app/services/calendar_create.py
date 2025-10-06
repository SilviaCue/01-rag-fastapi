import requests
from datetime import datetime
from typing import Optional, List
#calendar_create.py → solo se encarga de crear eventos (usa POST al script)
# URL del script de Google Apps para crear eventos en Google Calendar
CALENDAR_POST_URL = "https://script.google.com/macros/s/AKfycbzliMNV1Sz7zp844nRFz_KHy4yLkRAob6w_B4jCBOUT8BcbV5h7HDuuxzW9Uee8tu7wxw/exec"

#AKfycbzliMNV1Sz7zp844nRFz_KHy4yLkRAob6w_B4jCBOUT8BcbV5h7HDuuxzW9Uee8tu7wxw
# Función para crear un evento en Google Calendar
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
        # Realizar la solicitud POST al script de Google Apps
        response = requests.post(CALENDAR_POST_URL, json=datos, timeout=20)
        # Verificar si la solicitud fue exitosa
        response.raise_for_status()
        return response.text

    except Exception as e:
        return f"Error al crear evento: {str(e)}"
    
