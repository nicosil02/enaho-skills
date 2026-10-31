"""Grafica la pobreza monetaria por área, sexo o edad desde la base de personas."""
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

COLOR = "#B5451B"
TRAMOS = [0, 18, 30, 45, 60, 200]
NOMBRES_TRAMOS = ["0 a 17 años", "18 a 29 años", "30 a 44 años", "45 a 59 años", "60 años a más"]


def grupos(df, por):
    """Devuelve la serie de grupos, el texto del título y si conserva su orden natural."""
    if por == "area":
        return df.urbano.map({True: "Urbana", False: "Rural"}), "área de residencia", False
    if por == "sexo":
        return df.p207.map({1: "Hombres", 2: "Mujeres"}), "sexo", False
    edad = pd.cut(df.p208a, TRAMOS, right=False, labels=NOMBRES_TRAMOS)
    return edad, "grupo de edad", True


def pobreza_por_grupo(df, grupo):
    """Porcentaje de personas pobres por grupo, siempre ponderado con facpob07."""
    t = pd.DataFrame({"g": grupo, "w": df.facpob07, "wp": df.facpob07 * df.pobre}).dropna(subset=["g"])
    r = t.groupby("g", observed=True)[["w", "wp"]].sum()
    return 100 * r.wp / r.w


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # La consola de Windows no usa UTF-8
    sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--anio", type=int, required=True)
    p.add_argument("--por", choices=["area", "sexo", "edad"], required=True)
    p.add_argument("--salidas", type=Path, default=Path("salidas"))
    p.add_argument("--figuras", type=Path, default=Path("figuras"))
    a = p.parse_args()

    ruta = a.salidas / f"personas_{a.anio}.parquet"
    if not ruta.exists():
        sys.exit(f"ERROR: falta {ruta}. Usa primero la skill limpiando-enaho.")
    df = pd.read_parquet(ruta)
    grupo, texto, orden_natural = grupos(df, a.por)
    valores = pobreza_por_grupo(df, grupo)
    if not orden_natural:
        valores = valores.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7, 1.2 + 0.7 * len(valores)))
    y = range(len(valores))
    barras = ax.barh(y, valores.values, color=COLOR)
    ax.bar_label(barras, labels=[f"{v:.1f}%" for v in valores.values], padding=4)
    ax.set_yticks(y, labels=valores.index)
    ax.invert_yaxis()
    ax.set_xlim(0, valores.max() * 1.15)
    ax.xaxis.set_visible(False)
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.set_title(f"Pobreza monetaria por {texto}, Perú {a.anio}", loc="left", fontsize=12)
    fig.text(0.01, 0.01, f"Fuente: INEI, ENAHO {a.anio}", fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    a.figuras.mkdir(exist_ok=True)
    salida = a.figuras / f"pobreza_por_{a.por}_{a.anio}.png"
    fig.savefig(salida, dpi=200)
    for nombre, valor in valores.items():
        print(f"{nombre}: {valor:.1f}%")
    print(f"Guardado: {salida}")


if __name__ == "__main__":
    main()
