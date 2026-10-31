---
name: descargando-enaho
description: Descarga del portal del INEI los microdatos de la ENAHO de cualquier año entre 2004 y 2024 y los módulos que se pidan, explica para qué sirve cada módulo y baja el GeoJSON de los departamentos del Perú. Úsala cuando pidan bajar, descargar u obtener la ENAHO o los datos del INEI, cuando pregunten qué módulo contiene un tema, o cuando falten archivos en datos/.
argument-hint: [año] [módulos]
---
# Descargar la ENAHO

1. El año es obligatorio. Si el pedido no lo dice, pregúntalo. Nunca asumas uno.
2. Si el pedido no dice los módulos, corre uv run ${CLAUDE_SKILL_DIR}/scripts/descargar.py --listar, muestra los módulos con su utilidad, recomienda los que sirvan según el tema y espera a que el usuario elija.
3. Si el usuario ya dijo los módulos, o si te llama otra skill, no preguntes y descarga.
4. Corre exactamente: uv run ${CLAUDE_SKILL_DIR}/scripts/descargar.py --anio <año> --modulos <módulos>
5. Agrega --limites si van a hacer un mapa o si piden los límites departamentales.
6. Si el script termina en ERROR, muestra el mensaje y detente. No busques otros enlaces ni datos parecidos.
7. Responde con los archivos que imprimió el script. No los descomprimas.

Para analizar pobreza o personas casi siempre hacen falta el módulo 34 y el 02. Todo módulo se une con otros por conglome, vivienda y hogar, y los de personas además por codperso. Cada zip trae su diccionario en PDF.
