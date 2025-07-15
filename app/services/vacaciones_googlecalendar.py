import requests
from datetime import datetime, timedelta
from dateutil import parser

CALENDAR_JSON_URL = "https://script.google.com/macros/s/AKfycbwOFvO1lubR6wmOFVurpU92smy_ht0GVLbqIz4_b492onCt2L325o7AOLZcWyVRa3TMvQ/exec"

def obtener_periodos_evento(nombre_buscado, tipo_evento="vacaciones", anio=2025):
    try:
        response = requests.get(CALENDAR_JSON_URL, params={'anio': anio})
        response.raise_for_status()
        datos = response.json()

        nombre_buscado = nombre_buscado.strip().lower()
        resumen = []

        if nombre_buscado == "todos" and tipo_evento == "reuniones":
            for categorias in datos.values():
                for evento in categorias.get("reuniones", []):
                    fecha_inicio = parser.isoparse(evento["inicio"])
                    fecha_fin = parser.isoparse(evento["fin"])
                    duracion = (fecha_fin - fecha_inicio).days + 1
                    titulo = evento.get("titulo") or evento.get("summary") or "Sin título"
                    descripcion = evento.get("descripcion")
                    resumen.append((fecha_inicio, fecha_fin, duracion, titulo, descripcion))
            return resumen

        for nombre_key, categorias in datos.items():
            if nombre_key.strip().lower() == nombre_buscado:
                for evento in categorias.get(tipo_evento, []):
                    fecha_inicio_raw = parser.isoparse(evento["inicio"])
                    fecha_fin_raw = parser.isoparse(evento["fin"])
                    titulo = evento.get("titulo")
                    descripcion = evento.get("descripcion")

                    if tipo_evento == "reuniones":
                        duracion = (fecha_fin_raw - fecha_inicio_raw).days + 1
                        resumen.append((fecha_inicio_raw, fecha_fin_raw, duracion, titulo, descripcion))
                    else:
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
                        resumen.append((fecha_inicio, fecha_fin, duracion, titulo, descripcion))
                return resumen

        return []
    except Exception as e:
        print(f"Error al obtener eventos: {e}")
        return []

def obtener_lista_nombres_desde_calendar():
    try:
        response = requests.get(CALENDAR_JSON_URL)
        response.raise_for_status()
        datos = response.json()
        return [str(nombre).strip().lower() for nombre in datos.keys()]
    except Exception as e:
        print(f"Error al obtener nombres desde el calendario: {e}")
        return []

# --- Filtros adicionales ---
def filtrar_por_mes(resumen_dias, mes):
    return [evento for evento in resumen_dias if evento[0].month == mes or evento[1].month == mes]

def filtrar_por_semana(resumen_dias, year, week):
    return [evento for evento in resumen_dias if evento[0].isocalendar()[:2] == (year, week) or evento[1].isocalendar()[:2] == (year, week)]

def filtrar_por_dia(resumen_dias, fecha):
    return [evento for evento in resumen_dias if evento[0].date() <= fecha <= evento[1].date()]
