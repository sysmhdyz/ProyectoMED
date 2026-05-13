import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sistema_medico.db")

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
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente        TEXT NOT NULL,
            enfermedad      TEXT NOT NULL,
            probabilidad    REAL NOT NULL,
            sintomas_usados TEXT DEFAULT '',
            fecha           TEXT DEFAULT (date('now'))
        );
        CREATE TABLE IF NOT EXISTS historial (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente        TEXT NOT NULL,
            enfermedad      TEXT NOT NULL,
            probabilidad    REAL NOT NULL,
            sintomas_usados TEXT DEFAULT '',
            fecha           TEXT DEFAULT (date('now'))
        );
        CREATE TABLE IF NOT EXISTS catalogo_sintomas (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS motivos_cita (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            tipo   TEXT NOT NULL DEFAULT 'general'
        );
        CREATE TABLE IF NOT EXISTS citas (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente TEXT NOT NULL,
            medico   TEXT NOT NULL,
            motivo   TEXT NOT NULL DEFAULT '',
            fecha    TEXT NOT NULL,
            hora     TEXT NOT NULL,
            asistio  TEXT DEFAULT 'Pendiente',
            notas    TEXT DEFAULT '',
            UNIQUE(paciente, fecha, hora)
        );
    """)

    # Migración segura: columna enfermedad → motivo en citas si existe versión antigua
    try:
        cols = [r[1] for r in cur.execute("PRAGMA table_info(citas)").fetchall()]
        if "enfermedad" in cols and "motivo" not in cols:
            cur.execute("ALTER TABLE citas RENAME COLUMN enfermedad TO motivo")
            con.commit()
    except Exception:
        pass

    # Migración: agregar sintomas_usados a tablas existentes si no existe
    for tabla in ("diagnosticos", "historial"):
        try:
            cols = [r[1] for r in cur.execute(f"PRAGMA table_info({tabla})").fetchall()]
            if "sintomas_usados" not in cols:
                cur.execute(f"ALTER TABLE {tabla} ADD COLUMN sintomas_usados TEXT DEFAULT ''")
                con.commit()
        except Exception:
            pass

    # Usuarios base
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)",
            [("admin","1234","admin"), ("medico","1234","medico"), ("samh","1234","admin")]
        )

    # Catálogo de síntomas
    cur.execute("SELECT COUNT(*) FROM catalogo_sintomas")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT OR IGNORE INTO catalogo_sintomas (nombre) VALUES (?)", [
            ("Fiebre",), ("Tos",), ("Dolor de cabeza",), ("Fatiga",),
            ("Náuseas",), ("Mareos",), ("Dolor muscular",), ("Escalofríos",),
            ("Sudoración nocturna",), ("Pérdida de apetito",), ("Dificultad para respirar",),
            ("Dolor de garganta",), ("Congestión nasal",), ("Vómitos",), ("Diarrea",),
            ("Dolor abdominal",), ("Erupción cutánea",), ("Pérdida de olfato",),
        ])

    # Motivos de cita predeterminados
    cur.execute("SELECT COUNT(*) FROM motivos_cita")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT OR IGNORE INTO motivos_cita (nombre, tipo) VALUES (?, ?)", [
            ("Consulta general",                  "general"),
            ("Revisión de rutina",                "general"),
            ("Seguimiento de tratamiento",        "general"),
            ("Chequeo preventivo",                "general"),
            ("Urgencia / Emergencia",             "urgencia"),
            ("Prueba de laboratorio",             "estudio"),
            ("Prueba de imagen (Rx, TAC, Eco)",   "estudio"),
            ("Prueba de sangre completa",         "estudio"),
            ("Prueba de alergia",                 "estudio"),
            ("Vacunación",                        "preventivo"),
            ("Control de peso y nutrición",       "preventivo"),
            ("Salud mental / Psicología",         "especialidad"),
            ("Cardiología",                       "especialidad"),
            ("Dermatología",                      "especialidad"),
            ("Pediatría",                         "especialidad"),
            ("Ginecología / Obstetricia",         "especialidad"),
            ("Ortopedia / Traumatología",         "especialidad"),
            ("Neurología",                        "especialidad"),
            ("Oftalmología",                      "especialidad"),
        ])

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

# ── PACIENTES ────────────────────────────────────────
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

# ── MÉDICOS ──────────────────────────────────────────
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

# ── ENFERMEDADES ─────────────────────────────────────
def get_enfermedades():
    con = get_con()
    rows = con.execute("SELECT * FROM enfermedades").fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_enfermedad(nombre, descripcion):
    con = get_con()
    cur = con.cursor()
    cur.execute("INSERT INTO enfermedades (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
    eid = cur.lastrowid
    con.commit(); con.close()
    return eid

def eliminar_enfermedad(nombre):
    con = get_con()
    con.execute("DELETE FROM enfermedades WHERE nombre = ?", (nombre,))
    con.commit(); con.close()

# ── SÍNTOMAS ─────────────────────────────────────────
def get_sintomas_de_enfermedad(enfermedad_id):
    con = get_con()
    rows = con.execute("SELECT * FROM sintomas WHERE enfermedad_id = ?", (enfermedad_id,)).fetchall()
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
        FROM sintomas s JOIN enfermedades e ON s.enfermedad_id = e.id
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]

# ── CATÁLOGO SÍNTOMAS ────────────────────────────────
def get_catalogo_sintomas():
    con = get_con()
    rows = con.execute("SELECT * FROM catalogo_sintomas ORDER BY nombre ASC").fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_sintoma_catalogo(nombre):
    con = get_con()
    try:
        con.execute("INSERT INTO catalogo_sintomas (nombre) VALUES (?)", (nombre,))
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        con.close()

# ── MOTIVOS DE CITA ──────────────────────────────────
def get_motivos_cita():
    con = get_con()
    rows = con.execute("SELECT * FROM motivos_cita ORDER BY tipo, nombre").fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_motivo_cita(nombre, tipo="general"):
    con = get_con()
    try:
        con.execute("INSERT INTO motivos_cita (nombre, tipo) VALUES (?, ?)", (nombre, tipo))
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        con.close()

def eliminar_motivo_cita(motivo_id):
    con = get_con()
    con.execute("DELETE FROM motivos_cita WHERE id = ?", (motivo_id,))
    con.commit(); con.close()

# ── DIAGNÓSTICOS / HISTORIAL ─────────────────────────
def get_diagnosticos():
    con = get_con()
    rows = con.execute("SELECT * FROM diagnosticos ORDER BY id DESC").fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_diagnostico(paciente, enfermedad, probabilidad, sintomas_usados=""):
    sint_str = sintomas_usados if isinstance(sintomas_usados, str) else ", ".join(sintomas_usados)
    con = get_con()
    con.execute(
        "INSERT INTO diagnosticos (paciente, enfermedad, probabilidad, sintomas_usados) VALUES (?, ?, ?, ?)",
        (paciente, enfermedad, probabilidad, sint_str)
    )
    con.execute(
        "INSERT INTO historial (paciente, enfermedad, probabilidad, sintomas_usados) VALUES (?, ?, ?, ?)",
        (paciente, enfermedad, probabilidad, sint_str)
    )
    con.commit(); con.close()

def get_historial():
    con = get_con()
    rows = con.execute("SELECT * FROM historial ORDER BY id DESC").fetchall()
    con.close()
    return [dict(r) for r in rows]

# ── CITAS ─────────────────────────────────────────────
def get_citas():
    con = get_con()
    rows = con.execute("SELECT * FROM citas ORDER BY fecha ASC, hora ASC").fetchall()
    con.close()
    return [dict(r) for r in rows]

def agregar_cita(paciente, medico, motivo, fecha, hora, notas=""):
    con = get_con()
    try:
        con.execute(
            "INSERT INTO citas (paciente, medico, motivo, fecha, hora, notas) VALUES (?, ?, ?, ?, ?, ?)",
            (paciente, medico, motivo, fecha, hora, notas)
        )
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        con.close()

def actualizar_cita(cita_id, asistio, notas):
    con = get_con()
    con.execute("UPDATE citas SET asistio = ?, notas = ? WHERE id = ?", (asistio, notas, cita_id))
    con.commit(); con.close()

def actualizar_asistencia(cita_id, asistio):
    con = get_con()
    con.execute("UPDATE citas SET asistio = ? WHERE id = ?", (asistio, cita_id))
    con.commit(); con.close()

def eliminar_cita(cita_id):
    con = get_con()
    con.execute("DELETE FROM citas WHERE id = ?", (cita_id,))
    con.commit(); con.close()

def get_cita_by_id(cita_id):
    con = get_con()
    row = con.execute("SELECT * FROM citas WHERE id = ?", (cita_id,)).fetchone()
    con.close()
    return dict(row) if row else None

# ── LISTAS EN MEMORIA ─────────────────────────────────
usuarios = []; pacientes = []; medicos = []; enfermedades = []
sintomas = []; diagnosticos = []; historial = []; catalogo_sintomas = []
citas = []; motivos_cita = []

def cargar_todo():
    global usuarios, pacientes, medicos, enfermedades, sintomas
    global diagnosticos, historial, catalogo_sintomas, citas, motivos_cita
    usuarios          = get_usuarios()
    pacientes         = get_pacientes()
    medicos           = get_medicos()
    enfermedades      = get_enfermedades()
    sintomas          = get_todos_sintomas()
    diagnosticos      = get_diagnosticos()
    historial         = get_historial()
    catalogo_sintomas = get_catalogo_sintomas()
    citas             = get_citas()
    motivos_cita      = get_motivos_cita()

init_db()
cargar_todo()
