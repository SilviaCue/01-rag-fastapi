import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from typing import Optional
from docx import Document
from app.providers.gemini_multimodal import GeminiMultimodalExtractor

# Configuración OCR local (fallback)
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\\Program Files\\Tesseract-OCR\\tessdata"

class FileParser:
    def __init__(self, docs_raw_path: str):
        self.docs_raw_path = docs_raw_path
        self.gemini_extractor = GeminiMultimodalExtractor()

    def parse_document(self, filename: str) -> Optional[str]:
        file_path = os.path.join(self.docs_raw_path, filename)
        if not os.path.isfile(file_path):
            print(f"Archivo no encontrado: {file_path}")
            return None

        ext = filename.lower().split(".")[-1]
        if ext == "pdf":
            return self._extract_text_from_pdf(file_path, filename)
        elif ext == "docx":
            return self._extract_text_from_docx(file_path)
        else:
            print(f"Formato no soportado: {filename}")
            return None

    def _extract_text_from_pdf(self, file_path: str, original_filename: str) -> str:
        txt_path = os.path.join("storage/docs_chunks", original_filename.replace(".pdf", ".txt"))
        if os.path.exists(txt_path):
            print(f"Ya existe el TXT de {original_filename}, se omite Gemini.")
            return ""

        texto_total = ""
        prompt = """
Extrae TODO el texto visible en esta imagen escaneada de un documento técnico.
- El texto está en español.
- Extrae cuidadosamente cualquier dirección URL, incluso si está resaltada o en color.
- Respeta la estructura: títulos, párrafos, saltos de línea y sangrías.
- No inventes contenido. No completes frases ni rellenes huecos.
- Si hay tablas o listas, representa su contenido como texto plano.
- Devuelve solo texto, sin explicaciones ni resúmenes.
"""

        with fitz.open(file_path) as doc:
            for i, page in enumerate(doc):
                img_path = f"temp_page_{i}.png"
                try:
                    pix = page.get_pixmap(dpi=300)
                    pix.save(img_path)

                    # Convertir a escala de grises + binarización fuerte
                    image = Image.open(img_path).convert("L")
                    image = image.point(lambda x: 0 if x < 180 else 255, '1')
                    image.save(img_path)

                    print(f"[Gemini] Procesando página {i} de {file_path}...")
                    try:
                        ocr_response = self.gemini_extractor.model.generate_content([prompt, image])
                        ocr_text = ocr_response.text.strip() if ocr_response.text else ""
                    except Exception as e:
                        print(f"⚠️ Error Gemini: {e}")
                        ocr_text = ""

                    # Guardar TXT por página si Gemini devuelve algo
                    if ocr_text and ocr_text.strip():
                        page_txt_path = os.path.join(
                            "storage/docs_chunks", f"{original_filename.replace('.pdf', '')}_p{i}_gemini.txt"
                        )
                        with open(page_txt_path, "w", encoding="utf-8") as f:
                            f.write(ocr_text)

                    # Fallback con Tesseract
                    if not ocr_text or not ocr_text.strip():
                        print("ℹ️ Usando Tesseract como respaldo...")
                        ocr_text = pytesseract.image_to_string(image, lang="spa")

                    texto_total += ocr_text + "\n\n"

                finally:
                    try:
                        os.remove(img_path)
                    except Exception:
                        pass

        texto_total = texto_total.strip()
        if texto_total:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(texto_total)

        return texto_total

    def _extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error leyendo Word: {e}")
            return ""
