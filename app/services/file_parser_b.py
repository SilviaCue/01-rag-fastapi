import os
import fitz  # PyMuPDF
from typing import Optional
import pytesseract
from PIL import Image
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"


class FileParser:

    def __init__(self, docs_raw_path: str):
        self.docs_raw_path = docs_raw_path

    def parse_document(self, filename: str) -> Optional[str]:
        file_path = os.path.join(self.docs_raw_path, filename)

        if not os.path.isfile(file_path):
            print(f"Archivo no encontrado: {file_path}")
            return None

        if filename.lower().endswith(".pdf"):
            return self._extract_text_from_pdf(file_path)
        else:
            print(f"Formato no soportado aún: {filename}")
            return None

    def _extract_text_from_pdf(self, file_path: str) -> str:
        texto_total = ""
        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():  # Si encuentra texto digital
                    texto_total += text
                else:
                    # Si no hay texto → aplicar OCR sobre la imagen de la página
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img, lang='spa')
                    texto_total += ocr_text
        return texto_total
