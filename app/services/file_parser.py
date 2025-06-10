# services/file_parser.py
#Leer texto desde PDF, Word, etc.
#uta: services/file_parser.py

import fitz  # PyMuPDF
import os

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text
