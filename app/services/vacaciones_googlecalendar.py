import requests
from datetime import datetime, timedelta
from dateutil import parser

CALENDAR_JSON_URL = "https://script.google.com/macros/s/AKfycbzmub9wwhq38XodVJuE1dRVRp4KU9uxP7GH2ySLp0IKU4sO7PkKYkp10W-vngSayrb7/exec"

# Devuelve quién está de vacaciones HOY
def obtener_vacaciones_desde_calendar():
    try:
        response = requests.get(CALENDAR_JSON_URL)
        response.raise_for_status()
        datos = response.json()
        
        # SNIPPET de depuración para Silvia
        if "silvia" in datos:
            print("[DEBUG] JSON de Silvia:", datos["silvia"])

        hoy = datetime.now().date()
        resultado = []

        for nombre, categorias in datos.items():
            for evento in categorias.get("vacaciones", []):
                fecha_inicio = datetime.fromisoformat(evento["inicio"]).date()
                fecha_fin = datetime.fromisoformat(evento["fin"]).date()
                print(f"[DEBUG] Evento: inicio={fecha_inicio}, fin={fecha_fin}")
                if fecha_inicio <= hoy <= fecha_fin:
                    resultado.append(nombre.strip().lower())

        return resultado

    except Exception as e:
        print(f"Error leyendo calendario: {e}")
        return []

# --- CAMBIO AQUI SOLO ---
# Ahora acepta "anio" como argumento (por defecto 2025) y lo pasa como parámetro GET a la URL
def obtener_periodos_vacaciones(nombre_buscado, anio=2025):
    try:
        response = requests.get(CALENDAR_JSON_URL, params={'anio': anio})
        response.raise_for_status()
        datos = response.json()

        nombre_buscado = nombre_buscado.strip().lower()

        for nombre_key, categorias in datos.items():
            if nombre_key.strip().lower() == nombre_buscado:
                resumen = []
                for evento in categorias.get("vacaciones", []):
                    fecha_inicio_raw = parser.isoparse(evento["inicio"])
                    fecha_fin_raw = parser.isoparse(evento["fin"])
                    # --- Ajuste para eventos de Google Calendar/UTC en España:
                    if fecha_inicio_raw.time() in [
                        datetime.strptime("22:00:00", "%H:%M:%S").time(),
                        datetime.strptime("23:00:00", "%H:%M:%S").time(),
                    ]:
                        fecha_inicio = (fecha_inicio_raw + timedelta(days=1)).date()
                    else:
                        fecha_inicio = fecha_inicio_raw.date()
                    if fecha_fin_raw.time() in [
                        datetime.strptime("22:00:00", "%H:%M:%S").time(),
                        datetime.strptime("23:00:00", "%H:%M:%S").time(),
                    ]:
                        fecha_fin = (fecha_fin_raw + timedelta(days=1)).date()
                    else:
                        fecha_fin = fecha_fin_raw.date()
                    if fecha_fin < fecha_inicio:
                        fecha_fin = fecha_inicio
                    duracion = (fecha_fin - fecha_inicio).days + 1
                    resumen.append((fecha_inicio, fecha_fin, duracion))
                return resumen

        return []

    except Exception as e:
        print(f"Error al obtener vacaciones: {e}")
        return []

# Devuelve lista de nombres válidos extraídos del JSON
def obtener_lista_nombres_desde_calendar():
    try:
        response = requests.get(CALENDAR_JSON_URL)
        response.raise_for_status()
        datos = response.json()

        if isinstance(datos, dict):
            return [str(nombre).strip().lower() for nombre in datos.keys()]

        if isinstance(datos, list):
            return [str(nombre).strip().lower() for nombre in datos if isinstance(nombre, str)]

        return []

    except Exception as e:
        print(f"Error al obtener nombres desde el calendario: {e}")
        return []
