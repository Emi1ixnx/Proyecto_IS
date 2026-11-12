-- Tablas del Sistema de Control de Asistencia v1.0 (SQLite).
-- Las fechas se guardan como texto AAAA-MM-DD.
-- dias_clase guarda números de día de la semana (0 = lunes ... 5 = sábado), p. ej. '0,2,4'.

CREATE TABLE IF NOT EXISTS materia (
    id_materia   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL,
    dias_clase   TEXT NOT NULL,
    fecha_inicio TEXT,
    fecha_fin    TEXT
);

CREATE TABLE IF NOT EXISTS alumno (
    id_alumno     INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_cuenta TEXT NOT NULL,
    nombre        TEXT NOT NULL,
    correo        TEXT NOT NULL,
    id_materia    INTEGER NOT NULL REFERENCES materia (id_materia),
    UNIQUE (id_materia, numero_cuenta)          -- RN03
);

CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_materia    INTEGER NOT NULL REFERENCES materia (id_materia),
    id_alumno     INTEGER NOT NULL REFERENCES alumno (id_alumno),
    fecha         TEXT NOT NULL,
    estado        TEXT NOT NULL CHECK (estado IN ('Presente', 'Ausente')),  -- RN06
    UNIQUE (id_alumno, fecha)                   -- RN07
);
