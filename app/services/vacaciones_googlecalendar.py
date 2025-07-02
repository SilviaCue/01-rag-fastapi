import requests
from datetime import datetime

# Sustituye por tu URL pública real del script de Apps Script:
CALENDAR_JSON_URL = "https://script.google.com/macros/s/AKfycbwR9LMxxnfcMSj575frqn77S1t0LneKEPRWDSH3ItX4tWb58Y6znBuX-dFKRt0rWpZYEg/exec"

def obtener_vacaciones_desde_calendar():
    try:
        response = requests.get(CALENDAR_JSON_URL)
        response.raise_for_status()
        eventos = response.json()

        hoy = datetime.now().date()
        resumen = []

        for evento in eventos:
            nombre = evento["titulo"].split("-")[0].strip().lower()
            fecha_inicio = datetime.fromisoformat(evento["inicio"]).date()
            fecha_fin = datetime.fromisoformat(evento["fin"]).date()

            if fecha_inicio <= hoy <= fecha_fin:
                resumen.append(nombre)

        return resumen

    except Exception as e:
        print(f"Error al leer eventos del calendario: {e}")
        return []
