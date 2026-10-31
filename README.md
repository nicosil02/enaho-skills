# Skills de Claude Code para la ENAHO

Cuatro skills que descargan, limpian, grafican y mapean la Encuesta Nacional de Hogares del INEI. Basta pedir en Claude Code un mapa de la pobreza por departamento para que las skills se encadenen y repliquen la cifra oficial.

| Skill | Entra | Sale |
|---|---|---|
| `descargando-enaho` | Un año y los módulos | Los zip en `datos/` y el GeoJSON si se pide |
| `limpiando-enaho` | Los módulos 34 y 02 | `salidas/personas_2024.parquet` y `salidas/validacion.txt` |
| `graficando-enaho` | La base limpia y un corte por área, sexo o edad | `figuras/*.png` |
| `mapeando-enaho` | La base limpia y el GeoJSON | `mapas/pobreza_departamento.png` |

## Cómo correrlo

Se necesita [uv](https://docs.astral.sh/uv/) y [Claude Code](https://code.claude.com/docs).

```bash
git clone <este repositorio>
cd enaho-skills
uv sync
claude
```

Dentro de Claude Code basta pedir

> Haz un mapa de la pobreza por departamento con la ENAHO 2024

Los datos no se suben al repositorio. La skill `descargando-enaho` los baja del portal de microdatos del INEI a la carpeta `datos/`. También se pueden correr los scripts sin Claude.

```bash
uv run .claude/skills/descargando-enaho/scripts/descargar.py --anio 2024 --modulos 34 02 --limites
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
uv run .claude/skills/graficando-enaho/scripts/graficar.py --anio 2024 --por area
uv run .claude/skills/mapeando-enaho/scripts/mapear.py --anio 2024
```

Para bajar a mano, cada módulo está en `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip`, donde 966 es el código de 2024 y 34 el módulo.

## Validación

La limpieza se detiene si no replica las cifras oficiales de 2024, y el resultado queda en `salidas/validacion.txt`.

| Cifra | Valor |
|---|---|
| Pobreza monetaria nacional | 27.6% |
| Pobreza extrema | 5.5% |
| Hogares en la sumaria | 33,691 |
| Residentes habituales | 108,664 |

El mapa también se detiene si un departamento se aleja 0.1 puntos o más de la referencia.

## Quién entra en el cálculo

Toda cifra se pondera con `facpob07` sobre los miembros del hogar, `p204 == 1`. Son las 109,842 personas que cuenta `mieperho`, y por eso la base de personas da la misma pobreza que la sumaria en todos los cortes. Los 108,664 residentes habituales se validan en `salidas/validacion.txt` y quedan marcados en la columna `residente`. Si la pobreza se calcula solo con ellos sale 27.53%, y Puno se aleja 0.5 puntos de la cifra oficial.

## Evaluación

`evaluacion.md` compara tres pedidos con y sin skills. Para repetirla hay que dar permisos a `claude -p`.

```bash
claude -p "Haz un mapa de la pobreza por departamento con la ENAHO 2024" --allowedTools "Bash,Read,Write,Edit,Glob,Grep"
claude -p --disallowedTools Skill "Haz un mapa de la pobreza por departamento con la ENAHO 2024" --allowedTools "Bash,Read,Write,Edit,Glob,Grep"
```
