from fastapi import APIRouter, HTTPException
import pandas as pd
from datetime import datetime

router = APIRouter()

CSV_URL = "https://docs.google.com/spreadsheets/d/17MfMq1GnBTLPI3uFVfzgqCx91Y1JEh6qtyGKqKPj3mo/export?format=csv&gid=0"

@router.get("/dias-vacaciones-drive/{nombre}")
def contar_dias_vacaciones_drive(nombre: str):
    try:
        df = pd.read_csv(CSV_URL, header=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo Google Sheets: {str(e)}")

    hoy = datetime.today()
    nombre_usuario = nombre.strip().lower()

    # Asumimos que las filas 3 a 62 contienen personas
    df_principal = df.iloc[3:62].copy()

    # Renombrar manualmente la primera columna
    df_principal.rename(columns={0: "Nombre"}, inplace=True)

    # Generar nombres de columnas: "Nombre", "Día_1", ..., hasta final
    columnas = ["Nombre"] + [f"Día_{i}" for i in range(1, df_principal.shape[1])]
    df_principal.columns = columnas

    if "Nombre" not in df_principal.columns:
        raise HTTPException(status_code=500, detail="No se encontró la columna 'Nombre' en el calendario")

    resultados = {
        "persona": nombre.capitalize(),
        "vacaciones_disfrutadas": 0,
        "vacaciones_reservadas": 0,
        "festivos_disfrutados": 0,
        "festivos_futuros": 0,
        "otros_permisos_disfrutados": 0,
        "otros_permisos_reservados": 0,
        "vacaciones_anteriores": 0,
        "restantes": None,
        "total_marcados": 0
    }

    encontrado = False

    for _, row in df_principal.iterrows():
        nombre_fila = str(row["Nombre"]).strip().lower()
        if nombre_fila == nombre_usuario:
            encontrado = True
            marcas = row.drop(labels=["Nombre"])

            for col, celda in marcas.items():
                if isinstance(celda, str):
                    letra = celda.strip().upper()
                    try:
                        num_dia = int(col.replace("Día_", ""))
                        fecha = datetime(hoy.year, 1, 1) + pd.to_timedelta(num_dia - 1, unit="D")
                    except:
                        continue

                    if letra == "H":
                        if fecha.date() <= hoy.date():
                            resultados["vacaciones_disfrutadas"] += 1
                        else:
                            resultados["vacaciones_reservadas"] += 1
                    elif letra == "F":
                        if fecha.date() <= hoy.date():
                            resultados["festivos_disfrutados"] += 1
                        else:
                            resultados["festivos_futuros"] += 1
                    elif letra == "A":
                        resultados["vacaciones_anteriores"] += 1
                    elif letra == "P":
                        if fecha.date() <= hoy.date():
                            resultados["otros_permisos_disfrutados"] += 1
                        else:
                            resultados["otros_permisos_reservados"] += 1

            print("Fila original para", nombre_fila)
            print(marcas.tolist())
            break

    if not encontrado:
        raise HTTPException(status_code=404, detail=f"No se encontró a {nombre} en la hoja de Drive")

    # Leer fila de totales (restantes)
    df_totales = df.iloc[63:].copy()
    df_totales.rename(columns={0: "Nombre"}, inplace=True)
    df_totales.columns = columnas[:df_totales.shape[1]]
    df_totales["Nombre"] = df_totales["Nombre"].astype(str).str.strip().str.lower()
    fila_total = df_totales[df_totales["Nombre"] == nombre_usuario]

    if not fila_total.empty:
        try:
            resultados["restantes"] = int(fila_total.iloc[0]["Día_1"])
        except:
            resultados["restantes"] = None

    resultados["total_marcados"] = sum([
        resultados["vacaciones_disfrutadas"],
        resultados["vacaciones_reservadas"],
        resultados["festivos_disfrutados"],
        resultados["festivos_futuros"],
        resultados["otros_permisos_disfrutados"],
        resultados["otros_permisos_reservados"],
        resultados["vacaciones_anteriores"]
    ])

    # Extra para depurar: ver cuántas columnas/días hay y fecha límite
    ult_dia = 1 + df.shape[1] - 2  # -1 por columna nombre, -1 porque Día_1 empieza en posición 1
    fecha_final = datetime(datetime.today().year, 1, 1) + pd.to_timedelta(ult_dia, unit="D")
    print("Días disponibles:", ult_dia)
    print("Último día representado en el Excel:", fecha_final.date())

    return resultados
