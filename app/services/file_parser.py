import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from typing import Optional
from docx import Document
from app.providers.gemini_multimodal import GeminiMultimodalExtractor

# Configuración OCR local (fallback)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"


class FileParser:
    def __init__(self, docs_raw_path: str):
        self.docs_raw_path = docs_raw_path
        self.gemini_extractor = GeminiMultimodalExtractor()

    def parse_document(self, filename: str) -> Optional[str]:
        """
        Decide cómo procesar el documento según su extensión.
        Solo soporta PDF y DOCX.
        """
        file_path = os.path.join(self.docs_raw_path, filename)

        if not os.path.isfile(file_path):
            print(f"Archivo no encontrado: {file_path}")
            return None

        ext = filename.lower().split(".")[-1]

        if ext == "pdf":
            return self._extract_text_from_pdf(file_path)
        elif ext == "docx":
            return self._extract_text_from_docx(file_path)
        else:
            print(f"Formato no soportado: {filename}")
            return None

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Procesa SIEMPRE cada página del PDF con Gemini multimodal.
        Si Gemini falla, usa OCR local (Tesseract).
        """
        texto_total = ""
        with fitz.open(file_path) as doc:
            for i, page in enumerate(doc):
                img_path = f"temp_page_{i}.png"
                try:
                    pix = page.get_pixmap(dpi=300)
                    pix.save(img_path)
                    
                    #mejora visual escala de grises y binario
                    image = Image.open(img_path).convert("L")  # Convertir a escala de grises
                    image = image.point(lambda x: 0 if x < 180 else 255, '1')  # Binarización
                    image.save(img_path)

                    # Gemini multimodal primero
                    print(f"[Gemini] Procesando página {i} de {file_path}...")
                    ocr_text = self.gemini_extractor.extract_text(img_path)

                    # Fallback Tesseract
                    if not ocr_text or not ocr_text.strip():
                        ocr_text = pytesseract.image_to_string(Image.open(img_path), lang="spa")

                    texto_total += ocr_text + "\n\n"

                finally:
                    try:
                        os.remove(img_path)
                    except Exception:
                        pass
        return texto_total.strip()

    def _extract_text_from_docx(self, file_path: str) -> str:
        """
        Extrae texto plano de un Word (docx).
        """
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error leyendo Word: {e}")
            return ""
