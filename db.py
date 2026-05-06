import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sistema_medico.db")

# =========================
# INICIALIZAR TABLAS
# =========================
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario  TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol      TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pacientes (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad   TEXT NOT NULL,
            sexo   TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS medicos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre       TEXT NOT NULL,
            especialidad TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS enfermedades (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            descripcion TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sintomas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            enfermedad_id INTEGER NOT NULL,
            nombre        TEXT NOT NULL,
            FOREIGN KEY (enfermedad_id) REFERENCES enfermedades(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS diagnosticos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente     TEXT NOT NULL,
            enfermedad   TEXT NOT NULL,
            probabilidad REAL NOT NULL,
            fecha        TEXT DEFAULT (date('now'))
        );
        CREATE TABLE IF NOT EXISTS historial (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente     TEXT NOT NULL,
            enfermedad   TEXT NOT NULL,
            probabilidad REAL NOT NULL,
            fecha        TEXT DEFAULT (date('now'))
        );
    """)
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)",
            [("admin","1234","admin"), ("medico","1234","medico"), ("samh","1234","admin")]
        )
    con.commit()
    con.close()

def get_con():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

# ── USUARIOS ─────────────────────────────────────────
def get_usuarios():
    con = get_con()
    rows = con.execute("SELECT * FROM usuarios").fetchall()
    con.close()
    return [dict(r) for r in rows]

# ── PACIENTES ─────────────────────────────────────────
def get_pacientes():
    con = get_con()
    rows = con.execute("SELECT * FROM pacientes").fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_paciente(nombre, edad, sexo):
    con = get_con()
    con.execute("INSERT INTO pacientes (nombre, edad, sexo) VALUES (?, ?, ?)", (nombre, edad, sexo))
    con.commit(); con.close()

def eliminar_paciente(nombre):
    con = get_con()
    con.execute("DELETE FROM pacientes WHERE nombre = ?", (nombre,))
    con.commit(); con.close()

# ── MÉDICOS ───────────────────────────────────────────
def get_medicos():
    con = get_con()
    rows = con.execute("SELECT * FROM medicos").fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_medico(nombre, especialidad):
    con = get_con()
    con.execute("INSERT INTO medicos (nombre, especialidad) VALUES (?, ?)", (nombre, especialidad))
    con.commit(); con.close()

def eliminar_medico(nombre):
    con = get_con()
    con.execute("DELETE FROM medicos WHERE nombre = ?", (nombre,))
    con.commit(); con.close()

# ── ENFERMEDADES ──────────────────────────────────────
def get_enfermedades():
    con = get_con()
    rows = con.execute("SELECT * FROM enfermedades").fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_enfermedad(nombre, descripcion):
    con = get_con()
    con.execute("INSERT INTO enfermedades (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
    con.commit(); con.close()

def eliminar_enfermedad(nombre):
    con = get_con()
    con.execute("DELETE FROM enfermedades WHERE nombre = ?", (nombre,))
    con.commit(); con.close()

# ── SÍNTOMAS (vinculados a enfermedad) ───────────────
def get_sintomas_de_enfermedad(enfermedad_id):
    con = get_con()
    rows = con.execute(
        "SELECT * FROM sintomas WHERE enfermedad_id = ?", (enfermedad_id,)
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_sintoma(enfermedad_id, nombre):
    con = get_con()
    con.execute("INSERT INTO sintomas (enfermedad_id, nombre) VALUES (?, ?)", (enfermedad_id, nombre))
    con.commit(); con.close()

def eliminar_sintoma(sintoma_id):
    con = get_con()
    con.execute("DELETE FROM sintomas WHERE id = ?", (sintoma_id,))
    con.commit(); con.close()

def get_todos_sintomas():
    con = get_con()
    rows = con.execute("""
        SELECT s.id, s.nombre, s.enfermedad_id, e.nombre AS enfermedad_nombre
        FROM sintomas s
        JOIN enfermedades e ON s.enfermedad_id = e.id
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]

# ── DIAGNÓSTICOS / HISTORIAL ──────────────────────────
def get_diagnosticos():
    con = get_con()
    rows = con.execute("SELECT * FROM diagnosticos ORDER BY id DESC").fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_diagnostico(paciente, enfermedad, probabilidad):
    con = get_con()
    con.execute("INSERT INTO diagnosticos (paciente, enfermedad, probabilidad) VALUES (?, ?, ?)",
                (paciente, enfermedad, probabilidad))
    con.execute("INSERT INTO historial (paciente, enfermedad, probabilidad) VALUES (?, ?, ?)",
                (paciente, enfermedad, probabilidad))
    con.commit(); con.close()

def get_historial():
    con = get_con()
    rows = con.execute("SELECT * FROM historial ORDER BY id DESC").fetchall()
    con.close()
    return [dict(r) for r in rows]

# ── LISTAS EN MEMORIA ─────────────────────────────────
usuarios     = []
pacientes    = []
medicos      = []
enfermedades = []
sintomas     = []
diagnosticos = []
historial    = []

def cargar_todo():
    global usuarios, pacientes, medicos, enfermedades, sintomas, diagnosticos, historial
    usuarios     = get_usuarios()
    pacientes    = get_pacientes()
    medicos      = get_medicos()
    enfermedades = get_enfermedades()
    sintomas     = get_todos_sintomas()
    diagnosticos = get_diagnosticos()
    historial    = get_historial()

init_db()
cargar_todo()
