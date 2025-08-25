from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()
# Ruta al archivo de vacaciones
VACACIONES_PATH = os.path.join(
    "storage", "docs_raw", "idearium", "rrhh", "vacaciones_personal", "vacacionesIdearium.xlsx"
)

# Carga una sola vez al inicio
try:
    excel_data = pd.read_excel(VACACIONES_PATH, sheet_name=None)
except Exception as e:
    excel_data = {}
    print(f"Error cargando Excel al inicio: {e}")
# Endpoint para contar días de vacaciones por persona
@router.get("/dias-vacaciones/{nombre}")
def contar_dias_vacaciones(nombre: str):
    if not excel_data:
        raise HTTPException(status_code=500, detail="Excel no cargado correctamente.")

    nombre = nombre.strip().capitalize()
    conteo = {"H": 0, "F": 0, "A": 0, "P": 0, "total": 0}
    encontrado = False

    for sheet_name, df_sheet in excel_data.items():
        df = df_sheet.iloc[3:].copy()
        df.columns = range(df.shape[1])
        df.rename(columns={0: "Nombre"}, inplace=True)

        for _, row in df.iterrows():
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
        raise HTTPException(status_code=404, detail=f"No se encontró a {nombre} en el archivo")

    return {
        "persona": nombre,
        "dias_vacaciones": conteo["H"],
        "festivos": conteo["F"],
        "vacaciones_anteriores": conteo["A"],
        "otros_permisos": conteo["P"],
        "total_marcados": conteo["total"]
    }
