from datetime import datetime, timedelta

# Aquí en el futuro iría el código que conecta con Google Calendar (API o App Script JSON)

def obtener_eventos_de_ejemplo():
    hoy = datetime.today().date()
    eventos = [
        {
            "persona": "ramiro",
            "fecha_inicio": hoy.isoformat(),
            "fecha_fin": (hoy + timedelta(days=2)).isoformat(),
            "descripcion": "Vacaciones"
        },
        {
            "persona": "ana",
            "fecha_inicio": (hoy + timedelta(days=5)).isoformat(),
            "fecha_fin": (hoy + timedelta(days=7)).isoformat(),
            "descripcion": "Permiso personal"
        }
    ]
    return eventos
