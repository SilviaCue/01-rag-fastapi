import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from app.providers.gemini_multimodal import GeminiMultimodalExtractor

# Configura Tesseract (OCR local de respaldo)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

# Ruta al PDF escaneado
pdf_path = "app/test/icearagon_manual.pdf"

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"No se encontró el PDF: {pdf_path}")

# Inicializa Gemini
extractor = GeminiMultimodalExtractor()

# Prompt detallado
prompt = """
Extrae TODO el texto visible en esta imagen escaneada de un documento técnico.
- El texto está en español.
- Extrae cuidadosamente cualquier dirección URL, incluso si está resaltada o en color.
- Respeta la estructura: títulos, párrafos, saltos de línea y sangrías.
- No inventes contenido. No completes frases ni rellenes huecos.
- Si hay tablas o listas, representa su contenido como texto plano.
- Devuelve solo texto, sin explicaciones ni resúmenes.
"""

texto_total = ""

# Procesar cada página como imagen
with fitz.open(pdf_path) as doc:
    for i, page in enumerate(doc):
        img_path = f"temp_page_{i}.png"
        try:
            print(f"\n🔍 Procesando página {i+1}...")

            pix = page.get_pixmap(dpi=300)
            pix.save(img_path)

            # Escala de grises + binarización fuerte
            image = Image.open(img_path).convert("L")
            image = image.point(lambda x: 0 if x < 180 else 255, '1')
            image.save(img_path)

            # Gemini primero
            try:
                response = extractor.model.generate_content([prompt, image])
                texto = response.text.strip() if response.text else ""
            except Exception as e:
                print(f"⚠️ Error Gemini: {e}")
                texto = ""

            # Fallback con Tesseract si no hay texto
            if not texto:
                print("ℹ️ Usando Tesseract como respaldo...")
                texto = pytesseract.image_to_string(image, lang="spa")

            texto_total += f"\n--- Página {i+1} ---\n{texto.strip()}\n"

        finally:
            if os.path.exists(img_path):
                os.remove(img_path)

# Mostrar todo el texto extraído
print("\n\n========= TEXTO EXTRAÍDO DEL PDF =========\n")
print(texto_total)
