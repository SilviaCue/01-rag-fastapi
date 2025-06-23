import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from typing import Optional
import pandas as pd
from docx import Document

# Configuración OCR
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

        ext = filename.lower().split(".")[-1]

        if ext == "pdf":
            return self._extract_text_from_pdf(file_path)
        elif ext == "docx":
            return self._extract_text_from_docx(file_path)
        elif ext in ("xls", "xlsx"):
            return self._extract_text_from_excel(file_path)
        elif ext in ("png", "jpg", "jpeg", "tif", "tiff"):
            return self._extract_text_from_image(file_path)
        else:
            print(f"Formato no soportado aún: {filename}")
            return None

    def _extract_text_from_pdf(self, file_path: str) -> str:
        texto_total = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text = page.get_text()
                if text.strip():
                    texto_total += text
                else:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img, lang='spa')
                    texto_total += ocr_text
        return texto_total

    def _extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error leyendo Word: {e}")
            return ""

    def _extract_text_from_excel(self, file_path: str) -> str:
        try:
            dfs = pd.read_excel(file_path, sheet_name=None)
            texto = ""
            for sheet_name, df in dfs.items():
                texto += f"\n--- Hoja: {sheet_name} ---\n"
                texto += df.astype(str).to_string(index=False)
            return texto
        except Exception as e:
            print(f"Error leyendo Excel: {e}")
            return ""

    def _extract_text_from_image(self, file_path: str) -> str:
        try:
            img = Image.open(file_path)
            return pytesseract.image_to_string(img, lang="spa")
        except Exception as e:
            print(f"Error OCR imagen: {e}")
            return ""
