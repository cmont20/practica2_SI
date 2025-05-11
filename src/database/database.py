import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data.db')

def init_db():
    """Crea la tabla USUARIO si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS USUARIO (
        ID_USUARIO INTEGER PRIMARY KEY AUTOINCREMENT,
        USERNAME TEXT UNIQUE NOT NULL,
        PASSWORD_HASH TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def get_db():
    init_db()      # <— Asegúrate de ejecutar esto antes de devolver la conexión
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Funciones de Usuario ---

def create_user(username, password):
    pw_hash = generate_password_hash(password)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO USUARIO (USERNAME, PASSWORD_HASH) VALUES (?, ?)",
            (username, pw_hash)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # usuario ya existe


def authenticate_user(username, password):
    db = get_db()
    row = db.execute(
        "SELECT ID_USUARIO, USERNAME, PASSWORD_HASH FROM USUARIO WHERE USERNAME = ?",
        (username,)
    ).fetchone()
    if row and check_password_hash(row['PASSWORD_HASH'], password):
        return {'id': row['ID_USUARIO'], 'username': row['USERNAME']}
    return None