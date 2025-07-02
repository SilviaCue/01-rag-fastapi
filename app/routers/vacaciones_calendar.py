from fastapi import APIRouter
from app.services.vacaciones_googlecalendar import obtener_vacaciones_desde_calendar

router = APIRouter()

@router.get("/vacaciones-hoy")
def vacaciones_hoy():
    eventos = obtener_vacaciones_desde_calendar()
    return {"eventos": eventos}
