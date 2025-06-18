from fastapi import APIRouter, UploadFile, File, HTTPException
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

@router.post("/upload-one/")
async def upload_one_document(file: UploadFile = File(...)):
    # Guardamos el PDF en docs_raw solo si no existe
    dest_path = os.path.join(DOCS_RAW, file.filename)

    if os.path.exists(dest_path):
        return {"message": f"El archivo '{file.filename}' ya existe y no se ha sobrescrito."}

    with open(dest_path, "wb") as buffer:
        buffer.write(await file.read())

    parser = FileParser(DOCS_RAW)
    splitter = TextSplitter(chunk_size=500)

    try:
        # Parseamos el documento
        text = parser.parse_document(file.filename)
        if not text:
            raise HTTPException(500, "No se pudo extraer texto del PDF")

        # Guardamos el TXT en docs_chunks
        txt_name = os.path.splitext(file.filename)[0].replace("/", "_") + ".txt"
        txt_path = os.path.join(DOCS_CHUNK, txt_name)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Indexamos
        document_id = file.filename.replace("\\", "/")
        chunks = splitter.split_text(text)
        vector_store.index_chunks(chunks, document_id=document_id)

        return {"message": f"Documento '{file.filename}' procesado e indexado correctamente."}

    except Exception as e:
        raise HTTPException(500, f"Error al procesar el documento: {str(e)}")
