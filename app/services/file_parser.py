import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from typing import Optional
import pandas as pd
from docx import Document
from odf.opendocument import load as odf_load
from odf import teletype
from odf.text import P, H
from app.providers.gemini_multimodal import GeminiMultimodalExtractor

# Configuración OCR local (fallback)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

class FileParser:
    def __init__(self, docs_raw_path: str):
        self.docs_raw_path = docs_raw_path
        self.gemini_extractor = GeminiMultimodalExtractor()  # ✅ crear una sola vez

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
        elif ext == "md":
            return self._extract_text_from_md(file_path)
        elif ext == "odt":
            return self._extract_text_from_odt(file_path)
        else:
            print(f"Formato no soportado aún: {filename}")
            return None

    # PDF: texto directo; si no hay, Gemini → fallback Tesseract
    def _extract_text_from_pdf(self, file_path: str) -> str:
        texto_total = ""
        with fitz.open(file_path) as doc:
            for i, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    texto_total += text
                else:
                    pix = page.get_pixmap(dpi=200)
                    img_path = f"temp_page_{i}.png"
                    pix.save(img_path)
                    try:
                        ocr_text = self.gemini_extractor.extract_text(img_path)
                        if not ocr_text or not ocr_text.strip():
                            ocr_text = pytesseract.image_to_string(Image.open(img_path), lang='spa')
                        texto_total += ocr_text
                    finally:
                        try:
                            os.remove(img_path)
                        except Exception:
                            pass
        return texto_total

    # DOCX: lectura directa
    def _extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error leyendo Word: {e}")
            return ""

    # Excel: concatenar hojas como texto
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

    # Imagen: Gemini → fallback Tesseract
    def _extract_text_from_image(self, file_path: str) -> str:
        try:
            text = self.gemini_extractor.extract_text(file_path)
            if text and text.strip():
                return text
        except Exception as e:
            print(f"Error Gemini multimodal: {e}")
        # Fallback
        try:
            img = Image.open(file_path)
            return pytesseract.image_to_string(img, lang="spa")
        except Exception as e:
            print(f"Error OCR imagen: {e}")
            return ""

    # Markdown: leer archivo (no usar Gemini aquí)
    def _extract_text_from_md(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error leyendo Markdown: {e}")
            return ""

    # ODT: usar odfpy sin acceder a .data
    def _extract_text_from_odt(self, file_path: str) -> str:
        try:
            doc = odf_load(file_path)

            # Intento 1: todo el texto de golpe
            try:
                raw = teletype.extractText(doc.text)
                if raw and raw.strip():
                    return raw
            except Exception:
                pass

            # Intento 2: recorrer cabeceras y párrafos
            textos = []

            for el in doc.getElementsByType(H):
                txt = teletype.extractText(el)
                if txt:
                    textos.append(txt)

            for el in doc.getElementsByType(P):
                txt = teletype.extractText(el)
                if txt:
                    textos.append(txt)

            return "\n".join(textos).strip()

        except Exception as e:
            print(f"Error leyendo ODT: {e}")
            return ""
