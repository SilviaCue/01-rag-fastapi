# app/routers/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
import os, shutil
from app.services.file_parser import FileParser

router = APIRouter()

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DOCS_RAW   = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_raw"))
DOCS_CHUNK = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_chunks"))

os.makedirs(DOCS_RAW, exist_ok=True)
os.makedirs(DOCS_CHUNK, exist_ok=True)

# De momento, desactivamos el endpoint de upload individual
#@router.post("/upload/")
#async def upload_document(file: UploadFile = File(...)):
   # """
   # Sube un único PDF, extrae su texto y guarda el .txt en storage/docs_chunks.
   # """
   # dest = os.path.join(DOCS_RAW, file.filename)
   # with open(dest, "wb") as buf:
       # shutil.copyfileobj(file.file, buf)

    #parser = FileParser(DOCS_RAW)
    #text = parser.parse_document(file.filename)
    #if not text:
       # raise HTTPException(500, "No se pudo extraer texto del PDF")

    #txt_name = os.path.splitext(file.filename)[0] + ".txt"
    #txt_path = os.path.join(DOCS_CHUNK, txt_name)
    #with open(txt_path, "w", encoding="utf-8") as f:
       # f.write(text)

    #return {"filename": file.filename, "text_file": txt_name}


@router.post("/upload-all/")
async def upload_all_documents():
    """
    Procesa todos los PDFs en storage/docs_raw y subcarpetas:
    extrae su texto y guarda el .txt en storage/docs_chunks.
    """
    if not os.path.isdir(DOCS_RAW):
        raise HTTPException(500, f"Directorio no encontrado: {DOCS_RAW}")

    import glob
    pdf_files = glob.glob(os.path.join(DOCS_RAW, '**', '*.pdf'), recursive=True)

    if not pdf_files:
        return {"message": "No se encontraron PDFs para procesar en docs_raw", "processed": 0, "errors": {}}

    parser    = FileParser(DOCS_RAW)
    processed = []
    errors    = {}

    for full_path in pdf_files:
        fname = os.path.relpath(full_path, DOCS_RAW)
        try:
            text = parser.parse_document(fname)
            if not text:
                errors[fname] = "No se extrajo texto"
                continue

            txt_name = os.path.splitext(fname)[0].replace(os.sep, "_") + ".txt"
            txt_path = os.path.join(DOCS_CHUNK, txt_name)
            os.makedirs(os.path.dirname(txt_path), exist_ok=True)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            processed.append(fname)

        except Exception as e:
            errors[fname] = str(e)

    return {
        "message": f"Procesados {len(processed)} documentos",
        "processed_files": processed,
        "errors": errors
    }



