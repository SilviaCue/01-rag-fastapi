

#endpoint /upload
# ruta routers/upload.py
#Subir archivos PDF, Word, etc.

from fastapi import APIRouter, UploadFile, File
import shutil
import os

router = APIRouter()

# Ruta absoluta basada en la ubicación real del archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_raw"))

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print("DEBUG — guardado en:", file_path)
    return {"filename": file.filename}






