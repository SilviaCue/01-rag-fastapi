from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_RAW_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_raw"))

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(DOCS_RAW_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)
