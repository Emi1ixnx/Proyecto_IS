"""Conexión a SQLite, creación de tablas y consultas de la aplicación."""

import sqlite3

from flask import current_app, g


# ------------------------------------------------------------------ Conexión
def get_db():
    """Una conexión por petición; las filas se pueden leer por nombre de columna."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def init_db():
    """Crea las tablas de schema.sql si todavía no existen."""
    with current_app.open_resource("schema.sql") as archivo:
        get_db().executescript(archivo.read().decode("utf-8"))


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
