# Cómo se guardan y se leen los días de clase (HU04-T01)

**Decisión:** los días de clase de una materia se guardan en la columna `materia.dias_clase`
como un `TEXT` con los números del día de la semana separados por comas, usando la misma
numeración que `date.weekday()` de Python:

| Número | Día       | Letra |
|:------:|-----------|:-----:|
| 0      | Lunes     | L     |
| 1      | Martes    | M     |
| 2      | Miércoles | M     |
| 3      | Jueves    | J     |
| 4      | Viernes   | V     |
| 5      | Sábado    | S     |

Ejemplo: una materia que se imparte lunes, miércoles y viernes se guarda como `"0,2,4"`.

**Por qué números y no letras:** L, M, M, J, V, S repite la «M» (martes y miércoles), así que
con letras no se podría saber a cuál se refiere. Con números, la validación es directa:
`fecha.weekday() in texto_a_dias(materia["dias_clase"])`.

**Funciones (en `db.py`):**

| Función                 | Entrada      | Salida                         | Uso                                  |
|-------------------------|--------------|--------------------------------|--------------------------------------|
| `dias_a_texto(dias)`    | `['2','0']`  | `'0,2'`                        | guardar en SQLite (ordenado, sin repetir) |
| `texto_a_dias(texto)`   | `'0,2,4'`    | `[0, 2, 4]`                    | comparar con `date.weekday()`        |
| `dias_legibles(texto)`  | `'0,2,4'`    | `'Lunes, Miércoles, Viernes'`  | mostrar en pantalla                  |
