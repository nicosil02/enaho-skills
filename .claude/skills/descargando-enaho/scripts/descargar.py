"""Descarga a datos/ los módulos de la ENAHO que se pidan y, si se pide, los límites departamentales.

Si un archivo ya está y es válido, no lo vuelve a bajar. Solo usa la biblioteca estándar.
"""
import argparse
import sys
import urllib.request
import zipfile
from pathlib import Path

# Código de cada año en el portal de microdatos del INEI, verificado dentro de cada zip
CODIGOS = {
    2004: 280, 2005: 281, 2006: 282, 2007: 283, 2008: 284, 2009: 285, 2010: 279,
    2011: 291, 2012: 324, 2013: 404, 2014: 440, 2015: 498, 2016: 546, 2017: 603,
    2018: 634, 2019: 687, 2020: 737, 2021: 759, 2022: 784, 2023: 906, 2024: 966,
}
# Catálogo de 2024: módulo -> (qué contiene, para qué sirve). Otros años pueden no traer todos.
MODULOS = {
    "01": ("Vivienda y hogar", "Materiales, agua, luz, desagüe y hacinamiento"),
    "02": ("Miembros del hogar", "Sexo, edad, parentesco y residencia de cada persona"),
    "03": ("Educación", "Nivel educativo, matrícula, asistencia y gasto escolar"),
    "04": ("Salud", "Enfermedad, atención médica, seguro de salud y gasto"),
    "05": ("Empleo e ingresos", "Ocupación, informalidad, horas e ingresos del trabajo"),
    "07": ("Gastos en alimentos y bebidas", "Consumo de alimentos del hogar. Es el módulo más pesado"),
    "08": ("Instituciones benéficas", "Ayuda alimentaria recibida por el hogar"),
    "09": ("Mantenimiento de la vivienda", "Gastos en reparación y limpieza de la vivienda"),
    "10": ("Transportes y comunicaciones", "Gastos en pasajes, combustible, teléfono e internet"),
    "11": ("Servicios a la vivienda", "Gastos en alquiler y servicios del hogar"),
    "12": ("Esparcimiento, diversión y cultura", "Gastos en recreación y cultura"),
    "13": ("Vestido y calzado", "Gastos en ropa y calzado"),
    "15": ("Gastos de transferencia", "Dinero que el hogar da a otros hogares o instituciones"),
    "16": ("Muebles y enseres", "Gastos en muebles y artefactos"),
    "17": ("Otros bienes y servicios", "Gastos que no entran en otras categorías"),
    "18": ("Equipamiento del hogar", "Artefactos y bienes que posee el hogar"),
    "22": ("Producción agrícola", "Tierras, parcelas y cosechas del productor agropecuario"),
    "23": ("Subproductos agrícolas", "Derivados de la producción agrícola"),
    "24": ("Producción forestal", "Valor de plantas y árboles aprovechados"),
    "25": ("Gastos agrícolas o forestales", "Costos de la actividad agrícola"),
    "28": ("Gastos pecuarios", "Alimentos y servicios veterinarios para animales"),
    "34": ("Sumaria", "Ingreso, gasto, pobreza y factor de cada hogar. Base de cualquier análisis de pobreza"),
    "37": ("Programas sociales", "Beneficiarios de programas alimentarios y no alimentarios"),
    "77": ("Trabajadores independientes", "Negocios, ventas, gastos y empleo del independiente"),
    "78": ("Cuidados personales", "Gastos en bienes y servicios de cuidado personal"),
    "84": ("Participación ciudadana", "Organizaciones sociales y participación en asuntos públicos"),
    "85": ("Gobernabilidad", "Percepción de democracia, instituciones y corrupción"),
    "1825": ("Ollas comunes", "Hogares que obtienen alimentos preparados de ollas comunes"),
}
URL_INEI = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{codigo}-Modulo{modulo}.zip"
URL_GEOJSON = (
    "https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
    "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson"
)


def zip_valido(ruta, anio):
    """True si el zip abre, no está dañado y trae un .dta de ese año."""
    try:
        with zipfile.ZipFile(ruta) as z:
            nombres = [n.rsplit("/", 1)[-1].lower() for n in z.namelist()]
            tiene_dta = any(n.endswith(".dta") and str(anio) in n for n in nombres)
            return tiene_dta and z.testzip() is None
    except (zipfile.BadZipFile, OSError):
        return False


def bajar(url, destino):
    """Baja a un .part y renombra al final: un corte nunca deja un archivo a medias."""
    parcial = destino.with_name(destino.name + ".part")
    pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(pedido, timeout=60) as r, open(parcial, "wb") as f:
        esperado = int(r.headers.get("Content-Length") or 0)
        while bloque := r.read(1024 * 1024):
            f.write(bloque)
    if esperado and parcial.stat().st_size != esperado:
        parcial.unlink()
        raise OSError(f"descarga incompleta de {url}")
    parcial.replace(destino)


def listar():
    print(f"Años disponibles: {min(CODIGOS)} a {max(CODIGOS)}")
    print("Módulo | Contenido | Para qué sirve")
    for modulo, (nombre, uso) in MODULOS.items():
        print(f"{modulo} | {nombre} | {uso}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # La consola de Windows no usa UTF-8
    sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--listar", action="store_true", help="muestra los módulos y termina")
    p.add_argument("--anio", type=int)
    p.add_argument("--modulos", nargs="*", default=[])
    p.add_argument("--limites", action="store_true", help="baja el GeoJSON de departamentos")
    p.add_argument("--destino", type=Path, default=Path("datos"))
    a = p.parse_args()

    if a.listar:
        listar()
        return
    if a.modulos and a.anio not in CODIGOS:
        sys.exit(f"ERROR: indica --anio entre {min(CODIGOS)} y {max(CODIGOS)}.")
    modulos = [m.zfill(2) for m in a.modulos]
    if desconocidos := [m for m in modulos if m not in MODULOS]:
        sys.exit(f"ERROR: módulos que no existen: {desconocidos}. Mira las opciones con --listar.")
    if not modulos and not a.limites:
        sys.exit("ERROR: indica --modulos, --limites o --listar.")

    a.destino.mkdir(parents=True, exist_ok=True)
    for modulo in modulos:
        codigo = CODIGOS[a.anio]
        ruta = a.destino / f"{codigo}-Modulo{modulo}.zip"
        if ruta.exists() and zip_valido(ruta, a.anio):
            print(f"Ya estaba: {ruta}")
            continue
        try:
            bajar(URL_INEI.format(codigo=codigo, modulo=modulo), ruta)
        except OSError as e:
            sys.exit(f"ERROR: no se pudo bajar el módulo {modulo} de {a.anio}: {e}")
        if not zip_valido(ruta, a.anio):
            sys.exit(f"ERROR: {ruta} llegó dañado o no trae datos de {a.anio}.")
        print(f"Descargado: {ruta} ({ruta.stat().st_size / 1e6:.1f} MB), {MODULOS[modulo][0]}")

    if a.limites:
        ruta = a.destino / "peru_departamental_simple.geojson"
        if ruta.exists() and ruta.stat().st_size > 0:
            print(f"Ya estaba: {ruta}")
            return
        try:
            bajar(URL_GEOJSON, ruta)
        except OSError as e:
            sys.exit(f"ERROR: no se pudo bajar el GeoJSON: {e}")
        print(f"Descargado: {ruta} ({ruta.stat().st_size / 1e3:.0f} KB)")


if __name__ == "__main__":
    main()
