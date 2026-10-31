---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI y arma una base de personas con pobreza y factor de expansión, validada contra la cifra oficial. Úsala cuando pidan limpiar, unir o analizar la ENAHO, o calcular pobreza por región, departamento, sexo o edad.
argument-hint: [año]
---
# Limpiar la ENAHO

1. Toma el año del pedido. Si no lo dice, pregúntalo.
2. Si faltan los módulos 34 o 02 de ese año en datos/, usa la skill descargando-enaho con ese año y esos dos módulos.
3. Corre exactamente: uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio <año>
4. Lee salidas/validacion.txt. Si el script termina en ERROR, detente y muestra qué prueba falló. Nunca ajustes filtros ni pesos para que cuadre.
5. Si el año no tiene cifras oficiales cargadas, avisa que la base no está validada.
6. Responde con salidas/personas_<año>.parquet. Toda cifra va ponderada con facpob07, nunca contando encuestas.
7. Antes de usar una variable que no está en la base, o de calcular una cifra por departamento, lee reference.md.
