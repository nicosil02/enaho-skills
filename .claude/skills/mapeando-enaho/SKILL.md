---
name: mapeando-enaho
description: Hace el mapa del Perú con la pobreza monetaria por departamento a partir de la ENAHO y el GeoJSON de límites, uniendo por código y validando los 25 departamentos contra la referencia oficial. Úsala cuando pidan un mapa, coropleta o comparación de la pobreza por departamento o región.
argument-hint: [año]
---
# Mapear la ENAHO

1. Toma el año del pedido. Si no lo dice, usa el de la única salidas/personas_*.parquet. Si no hay ninguna o hay varias, pregúntalo.
2. Si no existe salidas/personas_<año>.parquet, usa primero la skill limpiando-enaho.
3. Si falta datos/peru_departamental_simple.geojson, usa la skill descargando-enaho con --limites.
4. Corre exactamente: uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py --anio <año>
5. Si el script termina en ERROR, detente y muestra el mensaje. Nunca unas por nombre para arreglarlo.
6. Abre mapas/pobreza_departamento.png y revisa que se lea bien antes de responder.
7. Responde con los departamentos de mayor y menor pobreza, y la ruta del mapa.

## Reglas que el script ya cumple y no se cambian

- Une por código, ubigeo[:2] con FIRST_IDDP como texto. Nunca por nombre, porque APURIMAC no es Apurímac.
- Exige 25 departamentos y ninguno sin dato.
- Un color de claro a oscuro, desde 0. Nunca arcoíris.
- Leyenda con la unidad, % de personas.
- Lima (15) y Callao (07) van separados.
