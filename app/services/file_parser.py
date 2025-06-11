# app/services/file_parser.py

import os
import fitz  # PyMuPDF
from typing import Optional

class FileParser:

    def __init__(self, docs_raw_path: str):
        self.docs_raw_path = docs_raw_path

    def parse_document(self, filename: str) -> Optional[str]:
        file_path = os.path.join(self.docs_raw_path, filename)

        if not os.path.isfile(file_path):
            print(f" Archivo no encontrado: {file_path}")
            return None

        if filename.lower().endswith(".pdf"):
            return self._extract_text_from_pdf(file_path)
        else:
            print(f" Formato no soportado aún: {filename}")
            return None

    def _extract_text_from_pdf(self, file_path: str) -> str:
        texto_total = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                texto_total += page.get_text()
        return texto_total
