# app/routers/upload.py

from fastapi import APIRouter

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.get("/")
def test_upload():
    return {"message": "Ruta de /upload funcionando"}


