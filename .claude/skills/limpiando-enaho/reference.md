# Referencia de la base de personas

## Columnas de salidas/personas_<año>.parquet

| Columna | Qué es | Valores |
|---|---|---|
| conglome, vivienda, hogar | Llaves del hogar | Texto con ceros a la izquierda |
| codperso | Llave de la persona dentro del hogar | Texto |
| ubigeo | Distrito, seis dígitos | Texto |
| departamento | Primeros dos dígitos del ubigeo | Texto, 01 a 25 |
| dominio | Dominio geográfico | 8 es Lima Metropolitana |
| estrato | Tamaño del centro poblado | 1 a 8 |
| urbano | estrato menor o igual a 5 | True o False |
| pobreza | Situación de pobreza | 1 extremo, 2 no extremo, 3 no pobre |
| pobre | pobreza menor o igual a 2 | True o False |
| p203 | Parentesco con el jefe del hogar | Código |
| p207 | Sexo | 1 hombre, 2 mujer |
| p208a | Edad en años | Número |
| mieperho | Miembros del hogar según la sumaria | Número |
| factor07 | Factor de expansión del hogar | Número |
| facpob07 | Factor de expansión de la persona | Número |
| residente | Residente habitual | True o False |

## Quién está en la base

- La base trae a los miembros del hogar, p204 == 1, que en 2024 son 109,842 personas. Son exactamente los que cuenta mieperho en cada hogar, y sobre ellos el INEI mide la pobreza.
- La columna residente marca a los residentes habituales. El módulo 02 trae 108,664 en 2024, pero 609 de ellos no son miembros y por eso no están en la base.
- Si se calcula la pobreza solo con residentes habituales sale 27.53% y Puno da 40.4%. Con los miembros sale 27.58% y Puno da 39.9%, igual que la sumaria.
- facpob07 es igual a factor07 en estas personas, así que siempre se pondera con facpob07.

## Cómo calcular una tasa

```python
tasa = 100 * df.loc[df.pobre, "facpob07"].sum() / df["facpob07"].sum()
```

Nunca promedies la columna pobreza. Sus valores son categorías.

## Códigos que suelen confundir

- Lima es 15 y Callao es 07. Son departamentos distintos.
- El módulo 02 trae 117,721 filas en 2024. Muchas son personas que no son miembros del hogar.
- Otras variables están en los módulos que lista la skill descargando-enaho. Cada zip trae su diccionario en PDF.
