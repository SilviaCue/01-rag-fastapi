import pandas as pd
import os

ruta = "storage/docs_raw/idearium/rrhh/vacaciones_personal/vacacionesIdearium.xlsx"
nombres_cache = None

def obtener_nombres_vacaciones():
    global nombres_cache
    if nombres_cache is not None:
        return nombres_cache

    if not os.path.isfile(ruta):
        return []

    nombres = set()
    try:
        excel = pd.read_excel(ruta, sheet_name=None)
        for nombre_hoja, df in excel.items():
            for valor in df.values.flatten():
                if isinstance(valor, str):
                    val = valor.strip()
                    if val and val.lower() not in ("v", "f", "a", "p", "total", "enero", "febrero",
                                                   "marzo", "abril", "mayo", "junio", "julio",
                                                   "agosto", "septiembre", "octubre", "noviembre",
                                                   "diciembre", "l", "m", "x", "j", "s", "d", "restantes"):
                        nombres.add(val.lower())
    except Exception as e:
        print(f"Error leyendo Excel para nombres: {e}")
        return []

    nombres_cache = list(nombres)
    return nombres_cache
