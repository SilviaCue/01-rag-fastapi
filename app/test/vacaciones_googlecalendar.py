import requests
from datetime import datetime

CALENDAR_JSON_URL = "https://script.google.com/macros/s/AKfycbwR9LMxxnfcMSj575frqn77S1t0LneKEPRWDSH3ItX4tWb58Y6znBuX-dFKRt0rWpZYEg/exec"

def test_listar_eventos():
    try:
        response = requests.get(CALENDAR_JSON_URL)
        response.raise_for_status()
        eventos = response.json()

        print("---- EVENTOS DEL CALENDARIO ----")
        for evento in eventos:
            titulo = evento.get("titulo", "sin título")
            inicio = evento.get("inicio", "sin fecha")
            fin = evento.get("fin", "sin fecha")
            print(f"Título: {titulo} | Inicio: {inicio} | Fin: {fin}")
    except Exception as e:
        print(f"Error al leer eventos: {e}")

def test_filtrar_vacaciones_ramiro():
    try:
        nombre_buscado = "ramiro"
        response = requests.get(CALENDAR_JSON_URL)
        response.raise_for_status()
        eventos = response.json()

        resumen = []

        for evento in eventos:
            titulo = evento.get("titulo", "")
            if nombre_buscado not in titulo.lower():
                continue
            if "vacacion" not in titulo.lower():
                continue

            fecha_inicio = datetime.fromisoformat(evento["inicio"]).date()
            fecha_fin = datetime.fromisoformat(evento["fin"]).date()
            duracion = (fecha_fin - fecha_inicio).days + 1
            resumen.append((fecha_inicio, fecha_fin, duracion))

        print("\n---- VACACIONES DE RAMIRO ----")
        if not resumen:
            print("No se encontraron vacaciones.")
        else:
            for inicio, fin, dias in resumen:
                print(f"Del {inicio} al {fin} ({dias} días)")

    except Exception as e:
        print(f"Error en test de vacaciones: {e}")


# Ejecutar manualmente
if __name__ == "__main__":
    test_listar_eventos()
    test_filtrar_vacaciones_ramiro()
