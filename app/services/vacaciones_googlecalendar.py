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
# Días de vacaciones laborables anuales por defecto
DIAS_VACACIONES_POR_DEFECTO = 23

# Devuelve resumen con disfrutadas y pendientes
def obtener_resumen_vacaciones_con_pendientes(nombre, anio=2025):
    """
    Devuelve un resumen textual de vacaciones disfrutadas y días pendientes.
    """
    nombre = nombre.strip().lower()
    periodos = obtener_periodos_vacaciones(nombre, anio=anio)

    if not periodos:
        return f"No hay vacaciones registradas para {nombre.title()} en {anio}."

    total_disfrutados = 0
    detalles = []
    for inicio, fin, duracion in periodos:
        dias_laborables = 0
        for i in range(duracion):
            dia = inicio + timedelta(days=i)
            if dia.weekday() < 5:  # Lunes a Viernes
                dias_laborables += 1
        total_disfrutados += dias_laborables
        detalles.append(
            f"- Del {inicio.strftime('%d de %B')} al {fin.strftime('%d de %B')} ({dias_laborables} días laborables)"
        )

    pendientes = DIAS_VACACIONES_POR_DEFECTO - total_disfrutados
    if pendientes < 0:
        pendientes = 0

    resumen = (
        f"{nombre.title()} ha disfrutado de un total de {total_disfrutados} días laborables de vacaciones en {anio}:\n\n"
        + "\n".join(detalles)
        + f"\n\nTotal de días laborables disfrutados en {anio}: {total_disfrutados}\n"
        + f"Días pendientes en {anio}: {pendientes}"
    )

    return resumen
