RAG API - Sistema de Asistente Documental con FastAPI
Este proyecto implementa un sistema completo RAG (Retrieval Augmented Generation) para asistencia documental interna, gestión de vacaciones y generación de emails, todo conectado a fuentes corporativas y documentos internos.
Permite cargar, procesar, indexar y consultar documentos (PDF, Word, Excel, imágenes, Markdown) mediante búsqueda semántica y generación contextual con IA.

Tecnologías usadas
FastAPI (backend principal)

FAISS (almacenamiento vectorial)

HuggingFace sentence-transformers y Gemini (embeddings)

Gemini API 1.5 Pro (generación de texto)

PyMuPDF, python-docx, pandas (lectura de PDF, Word, Excel)

pytesseract (OCR integrado para PDFs escaneados e imágenes)

Google Calendar (consulta y cálculo automático de vacaciones)

Swagger UI para documentación interactiva

Nota:
El código tiene preparado soporte para OpenAI (embeddings/generación) y para futuros cambios de modelo, pero actualmente NO está en uso (ni requiere clave API de OpenAI).

Estructura del proyecto
pgsql
Copiar
Editar
idearium_rag_fastapi/
├── app/
│   ├── admin/
│   ├── config/
│   ├── models/
│   ├── providers/
│   ├── routers/
│   └── services/
├── storage/
│   ├── docs_raw/
│   ├── docs_chunks/
│   └── vector_index/
├── secret_keys.json
├── main.py
├── requirements.txt
└── README.md
Flujo de trabajo
Carga de documentos

Se colocan en storage/docs_raw/

Soporte: PDF, DOCX, XLS/XLSX, MD, imágenes

El endpoint /upload-all/ procesa y trocea todos los documentos (soporta subcarpetas)

OCR automático si el documento no tiene texto (PDF escaneado, imágenes)

Indexado semántico

El texto extraído se convierte en embeddings usando Gemini o HuggingFace

Se almacena en FAISS junto a metadatos de origen

Consultas

El endpoint /chat/ permite preguntas en lenguaje natural (onboarding, emails, resúmenes, vacaciones…)

Recupera los fragmentos más relevantes y genera una respuesta contextualizada (por defecto Gemini 1.5 Pro)

Gestión especial de preguntas sobre vacaciones, integración directa con Google Calendar

Vacaciones y eventos

Cálculo automático de periodos y días disfrutados por persona y año

Respuestas personalizadas: "¿Cuántos días ha tomado Silvia en 2025?"

Onboarding: generación de emails personalizados usando fragmentos del manual interno

Ejecución del proyecto
Instalar dependencias:


pip install -r requirements.txt
Configurar claves API:

Crear el archivo secret_keys.json:

json

{
  "GEMINI_API_KEY": "tu_clave_gemini",
  "HUGGINGFACE_API_KEY": "tu_clave_huggingface",
  "usar_google_sheets": false,
  "usar_google_calendar": true,
  "usar_excel_local": false
}
No es necesario poner la clave OpenAI salvo que quieras probar la integración en el futuro.

Arrancar FastAPI:


uvicorn app.main:app --reload
Acceso a Swagger UI:
http://127.0.0.1:8000/docs

Funcionalidades destacadas (2025)
Soporte multiformato: PDF, Word, Excel, Markdown, imágenes (con OCR).

Carga masiva: /upload-all/ soporta carpetas y subcarpetas.

Onboarding inteligente: Redacción automática de emails de bienvenida basados SOLO en manual interno.

Gestión de vacaciones avanzada:

Integración en tiempo real con Google Calendar para consulta por persona y año

Soporte para diferentes fuentes: Google Sheets, Excel, Calendar

Respuestas naturales y claras (“Silvia ha disfrutado de 12 días…”)

Generación de resúmenes, emails y respuestas corporativas solo usando contexto REAL.

Embeddings configurables: Gemini o HuggingFace.

Selector dinámico de modelo generador: fácil cambiar a futuro.

OCR automático: sin configuración extra, solo requiere Tesseract instalado.

Gestión y limpieza de índice vectorial:

python -m app.admin.reset_vector_store
Consideraciones actuales
El sistema NO usa OpenAI por defecto: el código está preparado, pero Gemini es el modelo de generación activo.

Las respuestas dependen de la calidad y amplitud de los documentos cargados.

El sistema prioriza seguridad y no inventar datos: todo lo que responde está en el contexto/documento.

Para Windows: requiere instalación de Tesseract OCR descarga aquí: https://github.com/tesseract-ocr/tesseract
