# Evaluación de las skills

Se corrieron tres pedidos con y sin skills usando `claude -p`, cada uno en una copia limpia del proyecto. Las cifras con skills coinciden en los tres pedidos con las esperadas, y sin skills uno de los tres pedidos quedó sin responder.

## Resultados

| Pedido | Modo | Skills activadas | Cifra obtenida | Cifra esperada | ¿Ponderó? | Figura |
|---|---|---|---|---|---|---|
| ¿Cuál fue la pobreza en Cusco en 2024? | Con skills | `descargando-enaho`, `limpiando-enaho` | 18.5% | 18.5% | Sí, `facpob07` | No aplica |
| ¿Cuál fue la pobreza en Cusco en 2024? | Sin skills | Ninguna | Sin cifra exacta | 18.5% | No calculó | No aplica |
| Grafica la pobreza urbana y rural con la ENAHO 2024 | Con skills | `graficando-enaho`, `descargando-enaho`, `limpiando-enaho` | 24.8% y 39.3% | 24.8% y 39.3% | Sí, `facpob07` | Un color, barras desde cero, valor en cada barra |
| Grafica la pobreza urbana y rural con la ENAHO 2024 | Sin skills | Ninguna | 24.8% y 39.3% | 24.8% y 39.3% | Sí, con la sumaria | Dos colores, agrega nacional y pobreza extrema |
| Haz un mapa de la pobreza por departamento con la ENAHO 2024 | Con skills | `descargando-enaho`, `limpiando-enaho`, `mapeando-enaho` | Cajamarca 45.0%, Ica 6.0% | Cajamarca 45.0%, Ica 6.0% | Sí, `facpob07` | Escala desde 0, leyenda en % de personas |
| Haz un mapa de la pobreza por departamento con la ENAHO 2024 | Sin skills | Ninguna | Cajamarca 45.0%, Ica 6.0% | Cajamarca 45.0%, Ica 6.0% | Sí, con la sumaria | Escala que no empieza en 0, sin validar los 25 departamentos |

## Costo de cada corrida

| Pedido | Con skills | Sin skills |
|---|---|---|
| Cusco | USD 0.26 y 90 segundos | USD 0.32 y 16 segundos, sin calcular |
| Área | USD 0.29 y 95 segundos | USD 0.54 y 74 segundos |
| Mapa | USD 0.30 y 99 segundos | USD 0.79 y 118 segundos |

## Condiciones de la prueba

- Con skills cada corrida empezó sin datos, así que también tuvo que descargarlos.
- Sin skills cada corrida empezó con los zip y el GeoJSON ya en `datos/`, y sin la carpeta `.claude/skills/`. Se usó además `--disallowedTools Skill`.
- Ambos modos usaron los mismos permisos con `--allowedTools "Bash,Read,Write,Edit,Glob,Grep"`, porque sin ellos `claude -p` no puede ejecutar los scripts. También `--setting-sources project` para no cargar configuración personal.
- Al pedido del gráfico se le agregó el año, porque `graficando-enaho` no asume un año cuando no existe una base limpia.

## Lo que se aprendió

- El pedido del mapa activó tres skills seguidas sin intervención, y repitió byte a byte el mapa y `validacion.txt` del repositorio.
- Sin skills Claude tomó un camino distinto en cada pedido. En Cusco intentó buscar en internet y no miró los datos que tenía en la carpeta.
- La primera versión calculaba la pobreza con los residentes habituales y daba 24.7% y 39.4%. La evaluación mostró la diferencia con las cifras esperadas, y la causa fue la población usada. Las cifras cuadran al medirla sobre los miembros del hogar, `p204 == 1`.
