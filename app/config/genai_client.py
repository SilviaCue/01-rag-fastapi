# app/config/genai_client.py
import google.generativeai as genai
from app.config.settings import GEMINI_API_KEY


def configure_genai():
    print("Configurando Gemini...")
    if not GEMINI_API_KEY:
        raise ValueError("Falta la variable GEMINI_API_KEY en el entorno")
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini configurado correctamente.")
    
# genai_client.py
# Configuración del cliente para el modelo generativo Gemini.
#
# Este archivo contiene la función configure_genai(), que inicializa y autentica la conexión con el servicio de IA Gemini,
# utilizando la clave de API configurada en settings.py.
#
# ¿Qué hace?
# - Importa la librería oficial de Google Generative AI (genai) y la clave de Gemini desde settings.
# - Proporciona la función configure_genai(), que debe llamarse antes de utilizar Gemini para asegurarse de que la API Key está presente y la conexión se establece correctamente.
# - Lanza un error claro si falta la clave de API, ayudando a identificar rápidamente problemas de configuración.
#
# Uso típico:
# Llama a configure_genai() al arrancar el sistema o antes de enviar peticiones a Gemini para asegurarte de que todo está correctamente configurado.

