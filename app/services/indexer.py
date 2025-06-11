import os
from app.services.file_parser import FileParser
from app.services.text_splitter import TextSplitter
from app.services.vector_store import VectorStore

class Indexer:

    def __init__(self, embedding_model: str = "huggingface"):
        self.splitter = TextSplitter(chunk_size=500, overlap=50)
        self.vector_store = VectorStore(embedding_model=embedding_model)
        self.file_parser = FileParser(docs_raw_path="storage/docs_raw")

    def index_document(self, filename: str):
        print(f" Indexando documento: {filename}")

        # Extraer texto con FileParser
        texto = self.file_parser.parse_document(filename)
        if not texto:
            print("No se pudo extraer texto del documento.")
            return

        # Dividir en chunks
        chunks = self.splitter.split_text(texto)
        print(f" Generados {len(chunks)} chunks.")

        # Indexar en el vector store
        self.vector_store.index_chunks(chunks, filename)
        print(" Documento indexado correctamente.")
