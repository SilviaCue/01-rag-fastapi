# test_parser.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.services.file_parser import FileParser

# Ruta a la carpeta donde tienes los archivos
DOCS_RAW_PATH = "storage/docs_raw"

# Instanciar el parser
parser = FileParser(docs_raw_path=DOCS_RAW_PATH)

# Recorrer todos los archivos de la carpeta
for filename in os.listdir(DOCS_RAW_PATH):
    file_path = os.path.join(DOCS_RAW_PATH, filename)
    
    if os.path.isfile(file_path):
        print(f"\n--- Procesando: {filename} ---")
        texto = parser.parse_document(filename)
        if texto:
            print(texto[:500])  # Muestra los primeros 500 caracteres
        else:
            print("No se pudo extraer texto.")
