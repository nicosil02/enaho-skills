"""Arma la base de personas de la ENAHO y la valida contra las cifras oficiales.

Entra: datos/<codigo>-Modulo34.zip y datos/<codigo>-Modulo02.zip
Sale: salidas/personas_<anio>.parquet y salidas/validacion.txt
"""
import argparse
import io
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

LLAVES = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES + ["codperso"]
OFICIAL = {2024: {"pobreza": 27.6, "extrema": 5.5, "hogares": 33691, "filas": 117721, "residentes": 108664}}
TOLERANCIA = 0.1


def leer(modulo, dta, datos):
    """Lee el .dta del año pedido sin importar el código del zip que lo trae."""
    for ruta in sorted(datos.glob(f"*-Modulo{modulo}.zip")):
        with zipfile.ZipFile(ruta) as z:
            for nombre in z.namelist():
                if nombre.rsplit("/", 1)[-1].lower() == dta:
                    with z.open(nombre) as f:
                        return pd.read_stata(io.BytesIO(f.read()), convert_categoricals=False)
    sys.exit(f"ERROR: falta {dta} en {datos}/. Descarga el módulo {modulo} de ese año.")


def normalizar(df):
    """Pasa las columnas a minúscula. La del año llega como aÑo y sin una codificación fija."""
    df.columns = [re.sub(r"^a.{1,2}o$", "anio", c.lower()) for c in df.columns]
    return df


def tasa(df, condicion, peso):
    return 100 * df.loc[condicion, peso].sum() / df[peso].sum()


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # La consola de Windows no usa UTF-8
    sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--anio", type=int, required=True)
    p.add_argument("--datos", type=Path, default=Path("datos"))
    p.add_argument("--salidas", type=Path, default=Path("salidas"))
    a = p.parse_args()

    sumaria = normalizar(leer("34", f"sumaria-{a.anio}.dta", a.datos))
    miembros = normalizar(leer("02", f"enaho01-{a.anio}-200.dta", a.datos))

    assert not sumaria.duplicated(LLAVES).any(), "hogares repetidos en la sumaria"
    assert not miembros.duplicated(LLAVES_PERSONA).any(), "personas repetidas en miembros"

    # Residente habitual es la definición de población. La pobreza del INEI se mide sobre los
    # miembros del hogar, p204 == 1, que son exactamente los que cuenta mieperho.
    miembros["residente"] = ((miembros.p204 == 1) & (miembros.p205 == 2)) | (
        (miembros.p204 == 2) & (miembros.p206 == 1)
    )
    personas = miembros[miembros.p204 == 1]
    por_hogar = personas.groupby(LLAVES).size().reindex(sumaria.set_index(LLAVES).index, fill_value=0)
    assert (por_hogar.values == sumaria.mieperho.values).all(), "mieperho no coincide con p204 == 1"

    columnas = LLAVES + ["ubigeo", "dominio", "estrato", "pobreza", "mieperho", "factor07"]
    base = personas[LLAVES_PERSONA + ["residente", "p203", "p207", "p208a", "facpob07"]].merge(
        sumaria[columnas], on=LLAVES, how="left", validate="m:1"
    )
    assert len(base) == len(personas), "la unión perdió o duplicó filas"
    assert base.pobreza.notna().all(), "hay personas sin hogar en la sumaria"
    assert base.ubigeo.str.len().eq(6).all(), "el ubigeo perdió ceros"

    base["departamento"] = base.ubigeo.str[:2]
    base["urbano"] = base.estrato <= 5
    base["pobre"] = base.pobreza <= 2
    base["anio"] = a.anio

    sumaria["peso"] = sumaria.factor07 * sumaria.mieperho
    pobreza_sumaria = tasa(sumaria, sumaria.pobreza <= 2, "peso")
    pobreza_personas = tasa(base, base.pobre, "facpob07")
    residentes = int(miembros.residente.sum())
    extrema = tasa(sumaria, sumaria.pobreza == 1, "peso")

    lineas = [
        f"ENAHO {a.anio}",
        f"Hogares en la sumaria: {len(sumaria):,}",
        f"Filas del módulo de miembros: {len(miembros):,}",
        f"Residentes habituales: {residentes:,}",
        f"Miembros del hogar, base de la pobreza: {len(base):,}",
        f"Pobreza con la sumaria, factor07 por mieperho: {pobreza_sumaria:.2f}%",
        f"Pobreza con personas, facpob07: {pobreza_personas:.2f}%",
        f"Pobreza extrema: {extrema:.2f}%",
    ]
    fallas = []
    oficial = OFICIAL.get(a.anio)
    if oficial is None:
        lineas.append(f"Sin cifras oficiales cargadas para {a.anio}. Base NO validada contra el INEI.")
    else:
        pruebas = [
            ("Pobreza con la sumaria", abs(pobreza_sumaria - oficial["pobreza"]) < TOLERANCIA),
            ("Pobreza con personas", abs(pobreza_personas - oficial["pobreza"]) < TOLERANCIA),
            ("Pobreza extrema", abs(extrema - oficial["extrema"]) < TOLERANCIA),
            ("Hogares", len(sumaria) == oficial["hogares"]),
            ("Filas de miembros", len(miembros) == oficial["filas"]),
            ("Residentes", residentes == oficial["residentes"]),
        ]
        fallas = [nombre for nombre, ok in pruebas if not ok]
        lineas += [f"{nombre}: {'OK' if ok else 'FALLA'}" for nombre, ok in pruebas]
        lineas.append(f"Referencia INEI {a.anio}: pobreza {oficial['pobreza']}%, residentes {oficial['residentes']:,}")

    a.salidas.mkdir(exist_ok=True)
    (a.salidas / "validacion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))
    if fallas:
        sys.exit(f"ERROR: no pasó la validación: {', '.join(fallas)}. No se guardó la base.")
    base.to_parquet(a.salidas / f"personas_{a.anio}.parquet", index=False)
    print(f"Guardado: {a.salidas / f'personas_{a.anio}.parquet'}")


if __name__ == "__main__":
    main()
