import requests
import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

RUTA_REPO = os.path.dirname(os.path.abspath(__file__))

def obtener_precios(fecha_str):
    start = fecha_str + "T00:00"
    end   = fecha_str + "T23:59"
    url   = "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real?start_date=" + start + "&end_date=" + end + "&time_trunc=hour"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    included = data.get("included", [])

    # Buscar cualquier indicador con valores
    valores = None
    tipo = ""
    for item in included:
        vals = item.get("attributes", {}).get("values", [])
        if vals and len(vals) > 0:
            valores = vals
            tipo = item.get("type", "?")
            break

    if not valores:
        raise ValueError("No hay datos de precio en la respuesta")

    # Agrupar por hora (por si vienen en intervalos de 15 min)
    horas = defaultdict(list)
    for v in valores:
        dt_str = v.get("datetime", "")
        if not dt_str:
            continue
        hora = datetime.fromisoformat(dt_str.replace("Z", ""))
        clave_hora = hora.strftime("%Y-%m-%dT%H:00:00")
        horas[clave_hora].append(v["value"])

    # Construir resultado con media de cada hora
    result = {}
    for clave_hora, vals in sorted(horas.items()):
        hora = datetime.fromisoformat(clave_hora)
        precio_medio = sum(vals) / len(vals)
        clave = hora.strftime("%H-%H")
        result[clave] = {
            "date": clave_hora + "+02:00",
            "price": round(precio_medio, 4),
            "is-cheap": precio_medio < 100,
            "source": tipo
        }

    return result

def main():
    print("Actualizador de precios PVPC (REE)")
    hoy    = datetime.now().strftime("%Y-%m-%d")
    manana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    precios = {}
    for fecha in [hoy, manana]:
        print("Obteniendo precios del " + fecha + "...", end=" ", flush=True)
        try:
            datos = obtener_precios(fecha)
            if datos:
                precios[fecha] = datos
                print("OK (" + str(len(datos)) + " horas)")
            else:
                print("Sin datos")
        except Exception as e:
            print("No disponible: " + str(e))

    if not precios:
        print("No se pudieron obtener precios.")
        sys.exit(1)

    print("Fechas obtenidas: " + ", ".join(precios.keys()))

    ruta_json = os.path.join(RUTA_REPO, "data", "prices.json")
    os.makedirs(os.path.dirname(ruta_json), exist_ok=True)
    with open(ruta_json, "w") as f:
        json.dump({"updated": datetime.now().isoformat(), "prices": precios}, f, indent=2)
    print("Guardado en " + ruta_json)
    print("Subiendo a GitHub...")
    try:
        os.chdir(RUTA_REPO)
        subprocess.run(["git", "add", "data/prices.json"], check=True)
        subprocess.run(["git", "commit", "-m", "Precios PVPC " + hoy], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Listo - precios publicados en tu web.")
    except subprocess.CalledProcessError as e:
        print("Error al subir a GitHub: " + str(e))

if __name__ == "__main__":
    main()
