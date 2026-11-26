from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
from pathlib import Path

url_base = "https://www.laliga.com/estadisticas/laliga-easports/goleadores/pagina/{}"
max_paginas = 31  # 606 jugadores / 20 por página

jugadores = []

for numero_pagina in range(1, max_paginas + 1):
    url = url_base.format(numero_pagina)
    respuesta = requests.get(url, timeout=15)
    respuesta.raise_for_status()

    html = respuesta.text
    pagina = BeautifulSoup(html, "html.parser")

    # La clasificación son 2 bloques: fichas[0] = columna NOMBRE, fichas[1] = EQUIPO | GAF | PJ | GPP
    fichas = pagina.select('[class="lp-w_100% lp-max-w_100%"]')
    if len(fichas) < 2:
        break  # página sin tabla: no hay más

    nombres = fichas[0].select('[class="lp-fw_400 lp-textStyle_text.sBold atom-text"]')
    filas = fichas[1].select("tr")[1:]  # [1:] para saltar la cabecera

    for nombre, fila in zip(nombres, filas):
        equipo = fila.select_one('[class="lp-fw_400 lp-textStyle_label.labelXSBold atom-text"]')
        numeros = fila.select('[class="lp-fw_400 lp-textStyle_text.sRegular atom-text"]')  # [GAF, PJ, GPP]

        if equipo is None or len(numeros) < 3:
            continue
        else:
            jugadores.append({
                "nombre": nombre.get_text(strip=True),
                "equipo": equipo.get_text(strip=True),
                "goles_a_favor": int(numeros[0].get_text(strip=True)),
                "partidos_jugados": int(numeros[1].get_text(strip=True)),
                "goles_por_partido": float(numeros[2].get_text(strip=True)),
            })

    print(f"Página {numero_pagina}: {len(filas)} jugadores")

    # La lista va ordenada por goles: si el último ya tiene 0, el resto también
    if not jugadores or jugadores[-1]["goles_a_favor"] == 0:
        break

    time.sleep(1)  # para no saturar la web

df_original = pd.DataFrame(jugadores)
df = df_original[df_original["goles_a_favor"] > 0]  # solo goleadores

print(df.to_string(index=False))
print(f"Total goleadores: {len(df)}")

carpeta_datos = Path(__file__).parent / "datos"
carpeta_datos.mkdir(exist_ok=True)  # crea la carpeta si no existe

df.to_csv(carpeta_datos / "goleadores_laliga.csv", index=False, encoding="utf-8-sig")
