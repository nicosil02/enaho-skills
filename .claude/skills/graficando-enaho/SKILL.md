---
name: graficando-enaho
description: Crea gráficos de barras de la pobreza monetaria del Perú con la ENAHO por área urbana y rural, sexo o grupo de edad, ponderados con el factor de expansión. Úsala cuando pidan graficar, comparar o visualizar la pobreza o la ENAHO.
argument-hint: [area|sexo|edad] [año]
---
# Graficar la ENAHO

1. Toma el año del pedido. Si no lo dice, usa el de la única salidas/personas_*.parquet. Si no hay ninguna o hay varias, pregúntalo.
2. Si no existe salidas/personas_<año>.parquet, usa primero la skill limpiando-enaho.
3. Elige el corte según la pregunta: area, sexo o edad.
4. Corre exactamente: uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --anio <año> --por <corte>
5. Abre el PNG y revisa que se lea bien antes de responder.
6. Responde con las cifras que imprimió el script y la ruta en figuras/.

## Reglas que el script ya cumple y no se cambian

- Pondera siempre con facpob07.
- Barras que empiezan en cero y ordenadas. La edad conserva su orden natural.
- Un solo color y el valor escrito en cada barra.
- El título dice qué y cuándo.
- Nota al pie con la fuente, INEI y ENAHO del año.
- PNG a 200 dpi en figuras/.

Si piden otro corte, haz un script nuevo que cumpla las mismas reglas.
