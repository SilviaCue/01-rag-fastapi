from app.services.indexer import Indexer

# Solo el nombre del archivo
ruta_pdf = "Emergencias-2012_24_3_181-8.pdf"

indexador = Indexer(embedding_model="huggingface")
indexador.index_document(ruta_pdf)
