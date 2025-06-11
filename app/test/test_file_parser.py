from app.services.file_parser import FileParser

# Cambia el nombre exacto del PDF subido
filename = "Emergencias-2012_24_3_181-8.pdf"

parser = FileParser(docs_raw_path="storage/docs_raw")

texto = parser.parse_document(filename)

if texto:
    print(" Texto extraído correctamente.")
    print("Primeros 500 caracteres:\n")
    print(texto[:500])
else:
    print(" Error al extraer texto.")
