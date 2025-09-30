RAG API - Sistema de Asistente Documental con FastAPI

Este proyecto implementa un sistema completo RAG (Retrieval Augmented Generation) para asistencia documental interna, gestión de vacaciones y generación de emails, todo conectado a fuentes corporativas y documentos internos. Permite cargar, procesar, indexar y consultar documentos (PDF, Word, Excel, imágenes, Markdown) mediante búsqueda semántica y generación contextual con IA.

---

### Tecnologías usadas
- FastAPI (backend principal)
- FAISS (almacenamiento vectorial)
- HuggingFace sentence-transformers y Gemini (embeddings)
- Gemini API 1.5 Pro (generación de texto)
- PyMuPDF, python-docx, pandas (lectura de PDF, Word, Excel)
- pytesseract (OCR integrado para PDFs escaneados e imágenes)
- Google Calendar (consulta y cálculo automático de vacaciones, creación de eventos)
- Sistema de notificaciones en Calendar:
- Email inmediato al crear un evento (forzado con MailApp.sendEmail)
- Recordatorio automático 24 h antes del evento
- Swagger UI para documentación interactiva

> Nota: El código tiene preparado soporte para OpenAI (embeddings/generación) y para futuros cambios de modelo, pero actualmente NO está en uso (ni requiere clave API de OpenAI).

---

### Estructura del proyecto
```
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
```

---

### Flujo de trabajo

#### Carga de documentos
- Se colocan en `storage/docs_raw/`
- Soporte: PDF, DOCX, XLS/XLSX, MD, imágenes
- El endpoint `/upload-all/` procesa y trocea todos los documentos (soporta subcarpetas)
- OCR automático si el documento no tiene texto (PDF escaneado, imágenes)

#### Indexado semántico
- El texto extraído se convierte en embeddings usando Gemini o HuggingFace
- Se almacena en FAISS junto a metadatos de origen

#### Consultas
- El endpoint `/chat/` permite preguntas en lenguaje natural (onboarding, emails, resúmenes, vacaciones…)
- Recupera los fragmentos más relevantes y genera una respuesta contextualizada (por defecto Gemini 1.5 Pro)
- Permite también crear reuniones y otros eventos directamente en Google Calendar con preguntas como:
  - "Pon una reunión chatRAG mañana a las 12"
  - "Pon un sprint el 2 de agosto a las 11"
- Endpoints disponibles para gestión documental y consultas:
  - **`/upload-one/`** → Subir y procesar un único documento (PDF/DOCX).
  - **`/upload-multiple/`** → Subir y procesar varios documentos en lote.
  - **`/status/`** → Consultar el número total de chunks indexados en FAISS.
  - **`/download/{filename}`** → Descargar un documento original desde `storage/docs_raw/`.
  - **`/dias-vacaciones/{nombre}`** → Consultar los días de vacaciones, festivos y permisos de una persona según el Excel interno.
  - **`/chat/`** → Consultas generales al sistema RAG (documentación, onboarding, emails, vacaciones, calendario).


#### Integración directa con Google Calendar
- Consulta de eventos existentes: vacaciones, reuniones, festivos, entregas, sprints
- Filtros dinámicos: día, semana, mes, próximo evento
- Creación automática de eventos:
  - **Título sugerido por IA** (el usuario puede **confirmarlo o cambiarlo** antes de crear)
  - **Confirmación en dos pasos**:
    1) Propuesta inicial con fecha/hora y **título sugerido**  
    2) **Confirmación final** para crear (`ok`, `vale`, `sí`, `confirmo`, `crear`, `crea`)
  - **Invitados**:
    - Se añaden automáticamente los definidos en `ALERT_EMAILS` (archivo `secret_keys.json`)
    - El usuario puede **añadir o quitar** invitados por email en cualquier momento:
      - `añade: persona@ejemplo.com, otra@ejemplo.com`
      - `quita: persona@ejemplo.com`
  - Email inmediato al crear
  - Recordatorio 24 h antes (automático en Calendar)


#### Onboarding y consultas de documentos
- Generación de emails personalizados usando fragmentos del manual interno.
- Consulta de documentos indexados en el sistema mediante preguntas en lenguaje natural.
- Soporte especial para documentos que contienen **descripciones de pasos a seguir con imágenes, pantallazos e indicaciones en vivo**, gracias a la integración con **Gemini Multimodal**.


---

### Ejecución del proyecto

**Instalar dependencias:**
```
pip install -r requirements.txt
```

**Configurar claves API:**
Crear el archivo `secret_keys.json`:
```json
{
  "GEMINI_API_KEY": "tu_clave_gemini",
  "HUGGINGFACE_API_KEY": "tu_clave_huggingface",
  "usar_google_sheets": false,
  "usar_google_calendar": true,
  "usar_excel_local": false,
  "ALERT_EMAILS": ["tu_email@empresa.com"]
}
```
No es necesario poner la clave OpenAI salvo que quieras probar la integración en el futuro.
ALERT_EMAILS: lista de correos que recibirán siempre la invitación inmediata al crear un evento.

**Arrancar FastAPI:**
```
uvicorn app.main:app --reload
```

**Acceso a Swagger UI:**
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Funcionalidades destacadas (2025)
- **Soporte multiformato**: PDF, Word, Excel, Markdown, imágenes (con OCR).
- **Carga masiva**: `/upload-all/` soporta carpetas y subcarpetas.
- **Onboarding inteligente**: emails de bienvenida generados solo con el manual interno.
- **Gestión de vacaciones avanzada**:
  - Integración en tiempo real con Google Calendar
  - Consulta por persona y año
  - Filtros por día, semana, mes
- **Gestión de calendario extendida**:
  - Categorías: vacaciones, reuniones, festivos, entregas, sprints
  - Creación de reuniones/eventos directamente desde preguntas en lenguaje natural
  - Notificación inmediata por email + recordatorio 24 h antes
- **Consultas RAG seguras**:
  - Respuestas naturales, contextuales y basadas únicamente en documentos internos
  - Cero invención de datos
- **Embeddings configurables**: Gemini o HuggingFace
- **Selector dinámico de modelo generador** (fácil cambio futuro)
- **OCR automático** (requiere Tesseract instalado en Windows/Linux)

#### Gestión y limpieza de índice vectorial:
```
python -m app.admin.reset_vector_store
```

---

### Consideraciones actuales
- **El sistema NO usa OpenAI por defecto** → Gemini es el modelo activo.
- **Para la creación de eventos necesitas**:
  - Calendar compartido o propio donde el script tenga permisos de edición
  - Configurar `ALERT_EMAILS` en `secret_keys.json`
  - El correo inmediato lo envía **MailApp** desde Google Apps Script
  - El recordatorio 24h lo gestiona **Google Calendar**
- **Requiere instalación de Tesseract OCR** en Windows/Linux  
  - [Descargar aquí](https://github.com/tesseract-ocr/tesseract)
