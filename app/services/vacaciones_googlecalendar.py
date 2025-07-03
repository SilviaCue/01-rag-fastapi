import requests
from datetime import datetime

CALENDAR_JSON_URL = "https://script.google.com/macros/s/AKfycbzyA1-ukfIpw-6TPCjIo-9_962WYz2wBmXOVmBDXqvecsLZODzGy2L32CiCq2jgPPc6ug/exec"

# Devuelve quién está de vacaciones HOY
def obtener_vacaciones_desde_calendar():
    try:
        response = requests.get(CALENDAR_JSON_URL)
        response.raise_for_status()
        datos = response.json()

        hoy = datetime.now().date()
        resultado = []

        for nombre, categorias in datos.items():
            for evento in categorias.get("vacaciones", []):
                fecha_inicio = datetime.fromisoformat(evento["inicio"]).date()
                fecha_fin = datetime.fromisoformat(evento["fin"]).date()
                if fecha_inicio <= hoy <= fecha_fin:
                    resultado.append(nombre.strip().lower())

        return resultado

    except Exception as e:
        print(f"Error leyendo calendario: {e}")
        return []

# Devuelve periodos de vacaciones de una persona
def obtener_periodos_vacaciones(nombre_buscado):
    try:
        response = requests.get(CALENDAR_JSON_URL)
        response.raise_for_status()
        datos = response.json()

        nombre_buscado = nombre_buscado.strip().lower()

        for nombre_key, categorias in datos.items():
            if nombre_key.strip().lower() == nombre_buscado:
                resumen = []
                for evento in categorias.get("vacaciones", []):
                    fecha_inicio = datetime.fromisoformat(evento["inicio"]).date()
                    fecha_fin = datetime.fromisoformat(evento["fin"]).date()
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
