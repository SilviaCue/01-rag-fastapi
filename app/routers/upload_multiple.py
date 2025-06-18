from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from app.services.file_parser import FileParser
from app.services.text_splitter import TextSplitter
from app.services.vector_store_singleton import vector_store_instance as vector_store

router = APIRouter()

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DOCS_RAW   = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_raw"))
DOCS_CHUNK = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_chunks"))

os.makedirs(DOCS_RAW, exist_ok=True)
os.makedirs(DOCS_CHUNK, exist_ok=True)

@router.post("/upload-multiple/")
async def upload_multiple_documents(files: List[UploadFile] = File(...)):

    parser = FileParser(DOCS_RAW)
    splitter = TextSplitter(chunk_size=500)

    processed = []
    errors = {}

    for file in files:
        dest_path = os.path.join(DOCS_RAW, file.filename)

        try:
            # Sobrescribe siempre el archivo PDF
            with open(dest_path, "wb") as f:
                f.write(await file.read())

            text = parser.parse_document(file.filename)
            if not text:
                errors[file.filename] = "No se extrajo texto"
                continue

            txt_name = os.path.splitext(file.filename)[0].replace("/", "_") + ".txt"
            txt_path = os.path.join(DOCS_CHUNK, txt_name)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            document_id = file.filename.replace("\\", "/")
            chunks = splitter.split_text(text)
            vector_store.index_chunks(chunks, document_id=document_id)

            processed.append({
                "documento": file.filename,
                "chunks_indexados": len(chunks)
            })

        except Exception as e:
            errors[file.filename] = str(e)

    return {
        "procesados": processed,
        "errores": errors,
        "resumen": {
            "total_recibidos": len(files),
            "exitosos": len(processed),
            "fallidos": len(errors)
        }
    }
