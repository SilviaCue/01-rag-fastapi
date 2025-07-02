from fastapi import APIRouter

router = APIRouter()

@router.get("/vacaciones-hoy")
def vacaciones_hoy():
    return {"mensaje": "Funciona correctamente desde Google Calendar"}
