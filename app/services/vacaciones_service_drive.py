import pandas as pd

CSV_URL = "https://docs.google.com/spreadsheets/d/17MfMq1GnBTLPI3uFVfzgqCx91Y1JEh6qtyGKqKPj3mo/export?format=csv&gid=0"
nombres_cache = None

def obtener_nombres_vacaciones_drive():
    global nombres_cache
    if nombres_cache is not None:
        print("Nombres leídos desde caché (Google Sheets)")
        return nombres_cache
    
    print("Leyendo nombres desde Google Sheets...")  
    nombres = set()
    try:
        df = pd.read_csv(CSV_URL)
        for valor in df.values.flatten():
            if isinstance(valor, str):
                val = valor.strip()
                if val and val.lower() not in (
                    "v", "f", "a", "p", "total", "enero", "febrero", "marzo", "abril", "mayo",
                    "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
                    "l", "m", "x", "j", "s", "d", "restantes"
                ):
                    nombres.add(val.lower())
    except Exception as e:
        print(f"Error leyendo Google Sheets: {e}")
        return []

    nombres_cache = list(nombres)
    return nombres_cache
