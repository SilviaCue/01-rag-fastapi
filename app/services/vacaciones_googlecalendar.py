import requests
from datetime import datetime, timedelta
from dateutil import parser
#vacaciones_googlecalendar.py → se encarga de leer/consultar eventos
# URL del script de Google Apps para obtener eventos en formato JSON
CALENDAR_JSON_URL = "https://script.google.com/macros/s/AKfycbzwM8osD7jWBqr3Dfsx_il59rEie4BE-oQ5usPDG0iNugiDEAbs50JKFsUKrqNiH8dQmg/exec"
# Función para obtener periodos de eventos desde Google Calendar
def obtener_periodos_evento(nombre_buscado, tipo_evento="vacaciones", anio=2025):
    try:
        response = requests.get(CALENDAR_JSON_URL, params={'anio': anio})
        response.raise_for_status()
        datos = response.json()
# Buscar eventos para el nombre especificado
        nombre_buscado = nombre_buscado.strip().lower()
        resumen = []
# Manejo especial para "todos" en ciertos tipos de eventos
        if nombre_buscado == "todos" and tipo_evento in ["reuniones", "entregas", "sprints", "festivos"]:
            for categorias in datos.values():
                for evento in categorias.get(tipo_evento, []):
                    fecha_inicio = parser.isoparse(evento["inicio"])
                    fecha_fin = parser.isoparse(evento["fin"])
                    duracion = (fecha_fin - fecha_inicio).days + 1
                    titulo = evento.get("titulo") or evento.get("summary") or "Sin título"
                    descripcion = evento.get("descripcion")
                    resumen.append((fecha_inicio, fecha_fin, duracion, titulo, descripcion))
            return resumen

        for nombre_key, categorias in datos.items():
            if nombre_key.strip().lower() == nombre_buscado:
                eventos_revisar = categorias.get(tipo_evento, [])

                for evento in eventos_revisar:
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

def filtrar_por_semana(resumen_dias, year, week):
    resultado = []
    for evento in resumen_dias:
        inicio = evento[0]
        fin = evento[1]

        if isinstance(inicio, datetime):
            inicio = inicio.date()
        if isinstance(fin, datetime):
            fin = fin.date()

        for dia in range((fin - inicio).days + 1):
            fecha_actual = inicio + timedelta(days=dia)
            anio_iso, semana_iso, _ = fecha_actual.isocalendar()
            if anio_iso == year and semana_iso == week:
                resultado.append(evento)
                break

    return resultado

def filtrar_por_dia(resumen_dias, fecha):
    resultado = []
    for evento in resumen_dias:
        inicio = evento[0].date() if isinstance(evento[0], datetime) else evento[0]
        fin = evento[1].date() if isinstance(evento[1], datetime) else evento[1]
        if inicio <= fecha <= fin:
            resultado.append(evento)
    return resultado