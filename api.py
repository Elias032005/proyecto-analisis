import requests
import json
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

carpeta_proyecto = Path(__file__).parent
load_dotenv(carpeta_proyecto / ".env")  # lee el token del archivo .env

carpeta_datos = carpeta_proyecto / "datos"
carpeta_datos.mkdir(exist_ok=True)  # crea la carpeta si no existe

url_post = "https://api.football-data.org/v4/competitions/PD/standings"
headers = { 'X-Auth-Token': os.getenv("FOOTBALL_DATA_TOKEN") }


respuesta_api = requests.get(url_post, headers=headers)
print(respuesta_api.json().keys())
for clave in respuesta_api.json()['standings']:
    print(clave)

datos = respuesta_api.json()
df_clasificacion = pd.json_normalize(datos['standings'][0]['table'])

df_clasificacion.to_csv(carpeta_datos / "clasificacion_laliga.csv", index=False)

print(df_clasificacion)
print(df_clasificacion.columns)

# 1. Segunda URL (partidos ya finalizados de LaLiga)
url_partidos = "https://api.football-data.org/v4/competitions/PD/matches?status=FINISHED"

# 2. Nueva petición (reutilizando tus mismos 'headers')
respuesta_partidos = requests.get(url_partidos, headers=headers)
datos_partidos = respuesta_partidos.json()

# 3. Segundo DataFrame (aquí la lista viene bajo la llave 'matches')
df_partidos = pd.json_normalize(datos_partidos['matches'])
print(df_partidos)

print(df_partidos.columns)

df_partidos.to_csv(carpeta_datos / "partidos_laliga.csv", index=False, encoding="utf-8")