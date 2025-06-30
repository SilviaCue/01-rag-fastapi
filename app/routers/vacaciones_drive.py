from fastapi import APIRouter, HTTPException
import pandas as pd
from datetime import datetime

router = APIRouter()

CSV_URL = "https://docs.google.com/spreadsheets/d/17MfMq1GnBTLPI3uFVfzgqCx91Y1JEh6qtyGKqKPj3mo/export?format=csv&gid=0"

@router.get("/dias-vacaciones-drive/{nombre}")
def contar_dias_vacaciones_drive(nombre: str):
    try:
        df = pd.read_csv(CSV_URL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo Google Sheets: {str(e)}")

    nombre = nombre.strip().capitalize()
    conteo = {"H": 0, "F": 0, "A": 0, "P": 0, "total": 0}
    encontrado = False

    df_principal = df.iloc[3:62]  # Ajusta si cambia el rango útil
    df_principal.columns = range(df_principal.shape[1])
    df_principal.rename(columns={0: "Nombre"}, inplace=True)

    for _, row in df_principal.iterrows():
        nombre_fila = str(row["Nombre"]).strip().capitalize()
        if nombre_fila == nombre:
            marcas = row[1:]
            vc = marcas.value_counts()
            conteo["H"] += int(vc.get("H", 0))
            conteo["F"] += int(vc.get("F", 0))
            conteo["A"] += int(vc.get("A", 0))
            conteo["P"] += int(vc.get("P", 0))
            conteo["total"] += int(vc.sum())
            encontrado = True

    if not encontrado:
        raise HTTPException(status_code=404, detail=f"No se encontró a {nombre} en la hoja de Drive")

    return {
        "persona": nombre,
        "dias_vacaciones": conteo["H"],
        "festivos": conteo["F"],
        "vacaciones_anteriores": conteo["A"],
        "otros_permisos": conteo["P"],
        "total_marcados": conteo["total"]
    }
