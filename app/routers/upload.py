# app/routers/upload.py

from fastapi import APIRouter, HTTPException
import os, glob
from app.services.file_parser import FileParser
from app.services.text_splitter import TextSplitter
from app.services.vector_store_singleton import vector_store_instance as vector_store


router = APIRouter()

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DOCS_RAW   = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_raw"))
DOCS_CHUNK = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_chunks"))

os.makedirs(DOCS_RAW, exist_ok=True)
os.makedirs(DOCS_CHUNK, exist_ok=True)

@router.post("/upload-all/")
async def upload_all_documents():
    if not os.path.isdir(DOCS_RAW):
        raise HTTPException(500, f"Directorio no encontrado: {DOCS_RAW}")

    # Extensiones soportadas
    extensiones = ["*.pdf", "*.docx", "*.xlsx", "*.xls", "*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff", "*.md"]

    # Buscar todos los archivos con extensiones soportadas
    all_files = []
    for ext in extensiones:
        all_files.extend(glob.glob(os.path.join(DOCS_RAW, '**', ext), recursive=True))

    if not all_files:
        return {"message": "No se encontraron documentos válidos", "processed": 0, "errors": {}}

    parser = FileParser(DOCS_RAW)
    splitter = TextSplitter(chunk_size=500)

    processed = []
    errors = {}

    for full_path in all_files:
        fname = os.path.relpath(full_path, DOCS_RAW)
        document_id = fname.replace("\\", "/")

        try:
            text = parser.parse_document(fname)
            if not text:
                errors[document_id] = "No se extrajo texto"
                continue

            txt_name = os.path.splitext(document_id)[0].replace("/", "_") + ".txt"
            txt_path = os.path.join(DOCS_CHUNK, txt_name)
            os.makedirs(os.path.dirname(txt_path), exist_ok=True)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            chunks = splitter.split_text(text)
            vector_store.index_chunks(chunks, document_id=document_id)

            processed.append(document_id)

        except Exception as e:
            errors[document_id] = str(e)

    return {
        "message": f"Procesados {len(processed)} documentos",
        "processed_files": processed,
        "errors": errors
    }
