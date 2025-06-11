from app.services.text_splitter import TextSplitter

texto = (
    "Este es un ejemplo de texto largo que vamos a dividir en pequeños fragmentos o chunks. "
    "Así es como preparamos el texto para generar embeddings y alimentar nuestro vector store. "
    "Cada chunk tendrá un tamaño limitado, con solapamiento para conservar el contexto."
) * 10  # para simular texto largo

splitter = TextSplitter(chunk_size=100, overlap=20)
chunks = splitter.split_text(texto)

print(f"Generados {len(chunks)} chunks.\n")
for i, chunk in enumerate(chunks[:5]):
    print(f"Chunk {i+1}: {chunk}\n")
