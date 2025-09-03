import os
from app.services.file_parser import FileParser
from app.services.text_splitter import TextSplitter
from app.services.vector_store import VectorStore

# Servicio para indexar documentos
class Indexer:

    def __init__(self, embedding_model: str = "huggingface"):
        self.splitter = TextSplitter(chunk_size=500, overlap=50)
        self.vector_store = VectorStore(embedding_model=embedding_model)
        self.file_parser = FileParser(docs_raw_path="storage/docs_raw")
        # Carpeta donde guardamos los .txt (igual que en upload.py)
        self.docs_chunk_path = "storage/docs_chunks"
        os.makedirs(self.docs_chunk_path, exist_ok=True)

    # Indexar un documento
    def index_document(self, filename: str):
        print(f" Indexando documento: {filename}")

        # Extraer texto con FileParser
        texto = self.file_parser.parse_document(filename)
        if not texto:
            print("No se pudo extraer texto del documento.")
            return

        # Guardar siempre el .txt (para depuración y para PDFs → Gemini)
        txt_name = os.path.splitext(filename)[0].replace("/", "_").replace("\\", "_") + ".txt"
        txt_path = os.path.join(self.docs_chunk_path, txt_name)
        try:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(texto)
        except Exception as e:
            print(f"AVISO: no se pudo guardar el TXT en {txt_path}: {e}")

        # Solo indexar DOCX en embeddings
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".docx":
            # Dividir en chunks
            chunks = self.splitter.split_text(texto)
            print(f" Generados {len(chunks)} chunks.")

            # Indexar en el vector store
            self.vector_store.index_chunks(chunks, filename)
            print(" Documento indexado correctamente.")
        else:
            # PDFs u otros → NO se indexan en embeddings
            print(f" Documento {filename} detectado como {ext} → NO se indexa en embeddings (solo guardo TXT).")
