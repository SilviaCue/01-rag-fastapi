
import json
import os

class SecretKeys:
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), '../../secret_keys.json')
        with open(path, 'r', encoding='utf-8') as f:
            keys = json.load(f)
        self.gemini_api_key = keys.get('GEMINI_API_KEY')
        self.huggingface_api_key = keys.get('HUGGINGFACE_API_KEY')
        self.openai_api_key= keys.get("OPENAI_API_KEY")
        
        
          # Fuentes de vacaciones
        self.usar_google_sheets = keys.get("usar_google_sheets", False)
        self.usar_google_calendar = keys.get("usar_google_calendar", True)
        self.usar_excel_local = keys.get("usar_excel_local", False)
        
        # Correos electrónicos para alertas
        self.alert_emails = keys.get("ALERT_EMAILS", [])

        
# secret_keys.py
# Gestiona la carga de claves y parámetros sensibles (API keys) desde secret_keys.json.
# Define la clase SecretKeys para acceder de forma segura a las credenciales 
# y opciones  para elegir la fuente de datos de vacaciones (Google Calendar, Google Sheets o Excel local).



