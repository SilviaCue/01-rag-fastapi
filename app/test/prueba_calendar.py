# test/prueba_calendar.py
from datetime import datetime, timedelta
from app.services.calendar_create import crear_evento_en_calendar

# Evento dentro de 2 horas, duración 1h
inicio = datetime.now().replace(second=0, microsecond=0) + timedelta(hours=2)
fin = inicio + timedelta(hours=1)

resultado = crear_evento_en_calendar(
    "PRUEBA_INVITACION",
    inicio,
    fin,
    guests=["silviacuegonzalez@gmail.com"]  # invitada directa para ver el email
)

print("Resultado:", resultado)
