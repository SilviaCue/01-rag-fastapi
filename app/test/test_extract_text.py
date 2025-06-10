from app.services.file_parser import extract_text_from_pdf
import os

# Ruta al archivo PDF que subiste (ajusta el nombre si es otro)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "storage", "docs_raw", "Emergencias-2012_24_3_181-8.pdf"))

# Extraer texto
text = extract_text_from_pdf(PDF_PATH)

# Mostrar parte del contenido
print("\nTexto extraído desde el PDF:\n")
print(text[:500])  # Solo los primer
