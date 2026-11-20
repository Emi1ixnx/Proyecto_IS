# Sistema de Control de Asistencia de Alumnos

Aplicación web hecha con Flask y SQLite para que un profesor registre sus materias y alumnos,
pase lista por fecha y consulte el resumen de asistencia.

## Cómo ejecutarla

```bash
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir http://127.0.0.1:5000 en el navegador. La base de datos (`asistencia.db`) se crea sola
la primera vez.

## Qué hace

| Pantalla     | Ruta          | Historias    |
|--------------|---------------|--------------|
| Materias     | `/materias`   | HU01         |
| Alumnos      | `/alumnos`    | HU02         |
| Pasar lista  | `/pasar-lista`| HU03, HU04, HU05 |
| Resumen      | `/resumen`    | HU06, HU07   |

Reglas principales: una materia necesita nombre y al menos un día de clase; el número de
cuenta no se repite dentro de una materia; solo se pasa lista en un día de clase (y dentro del
rango de fechas, si existe); solo hay una lista por materia y fecha; el porcentaje es
`asistencias del alumno / listas registradas de la materia * 100`.

## Estructura

```
asistencia/
├── app.py            # crea la app Flask y define las rutas
├── db.py             # conexión a SQLite y consultas
├── schema.sql        # tablas materia, alumno y asistencia
├── templates/        # base, materias, alumnos, pasar_lista y resumen
├── docs/             # diagrama de la BD (dbdiagram.io) y decisión de días de clase
└── tests/            # pruebas automáticas
```

## Pruebas

```bash
python -m unittest discover -s tests -t . -v
```

Equipo: Amanda, Emiliano, Julio Ian, y Rodrigo
