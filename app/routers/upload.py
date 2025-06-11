from fastapi import APIRouter, UploadFile, File
import shutil
import os

# Importamos la clase FileParser
from app.services.file_parser import FileParser

router = APIRouter()

# Ruta absoluta basada en la ubicación real del archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_raw"))
CHUNK_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_chunks"))

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Crear el parser
    parser = FileParser(UPLOAD_DIR)
    
    # Extraer texto
    text = parser.parse_document(file.filename)
    
    # Guardar texto en archivo .txt
    txt_filename = os.path.splitext(file.filename)[0] + ".txt"
    txt_path = os.path.join(CHUNK_DIR, txt_filename)
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(text)
        
    print("Guardado PDF:", file_path)
    print("Texto extraído en:", txt_path)

    return {
        "filename": file.filename,
        "text_file": txt_filename
    }








