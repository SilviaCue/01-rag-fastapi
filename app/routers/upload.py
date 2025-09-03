# app/routers/upload.py
from fastapi import APIRouter, HTTPException
import os
from app.services.file_parser import FileParser
from app.services.text_splitter import TextSplitter
from app.services.vector_store_singleton import vector_store_instance as vector_store

router = APIRouter()  # ¡IMPRESCINDIBLE!

# Rutas base
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DOCS_RAW   = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_raw"))
DOCS_CHUNK = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_chunks"))

os.makedirs(DOCS_RAW, exist_ok=True)
os.makedirs(DOCS_CHUNK, exist_ok=True)

# === CAMBIO 1: solo soportamos PDF y DOCX ===
SUPPORTED_EXTS = {
    ".pdf", ".docx"
}

@router.post("/upload-all/")
async def upload_all_documents():
    if not os.path.isdir(DOCS_RAW):
        raise HTTPException(status_code=500, detail=f"Directorio no encontrado: {DOCS_RAW}")

    # Recorre recursivamente storage/docs_raw
    all_files = []
    for root, _, files in os.walk(DOCS_RAW):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in SUPPORTED_EXTS:
                all_files.append(os.path.join(root, fname))

    if not all_files:
        return {"message": "No se encontraron documentos válidos", "processed": 0, "errors": {}}

    parser = FileParser(DOCS_RAW)
    splitter = TextSplitter(chunk_size=500)

    processed = []
    errors = {}

    for full_path in all_files:
        # document_id relativo a DOCS_RAW (con /)
        rel_path = os.path.relpath(full_path, DOCS_RAW)
        document_id = rel_path.replace("\\", "/")

        try:
            text = parser.parse_document(document_id)  # parse_document espera ruta relativa a DOCS_RAW
            if not text or not text.strip():
                errors[document_id] = "No se extrajo texto"
                continue

            # Guarda texto completo (útil para depurar)
            txt_name = os.path.splitext(document_id)[0].replace("/", "_") + ".txt"
            txt_path = os.path.join(DOCS_CHUNK, txt_name)
            os.makedirs(os.path.dirname(txt_path), exist_ok=True)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            # === CAMBIO 2: solo indexamos DOCX, PDFs no entran en embeddings ===
            ext = os.path.splitext(document_id)[1].lower()
            if ext == ".docx":
                chunks = splitter.split_text(text)
                vector_store.index_chunks(chunks, document_id=document_id)
            else:
                print(f"Documento PDF detectado: {document_id} → no se indexa en embeddings")

            processed.append(document_id)

        except Exception as e:
            errors[document_id] = str(e)

    return {
        "message": f"Procesados {len(processed)} documentos",
        "processed_files": processed,
        "errors": errors
    }
