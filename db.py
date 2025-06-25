import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            cur.execute(f.read())
        conn.commit()


def get_user_id(user_name: str) -> int | None:
    """Return the id for ``user_name`` or ``None`` if not found."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE name=%s", (user_name,))
        row = cur.fetchone()
        return row[0] if row else None


def create_user(user_name: str, password: str, pin: str) -> int:
    """Create a new user with ``password`` and ``pin`` and return its id."""
    password_hash = generate_password_hash(password)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (name, password_hash, pin) VALUES (%s, %s, %s) RETURNING id",
            (user_name, password_hash, pin),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id


def verify_user(user_name: str, password: str) -> bool:
    """Return ``True`` if ``password`` matches stored hash for ``user_name``."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT password_hash FROM users WHERE name=%s",
            (user_name,),
        )
        row = cur.fetchone()
        return check_password_hash(row[0], password) if row else False


def reset_password(user_name: str, pin: str, new_password: str) -> bool:
    """Update password if ``pin`` matches. Return ``True`` on success."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT pin FROM users WHERE name=%s", (user_name,))
        row = cur.fetchone()
        if not row or row[0] != pin:
            return False
        new_hash = generate_password_hash(new_password)
        cur.execute(
            "UPDATE users SET password_hash=%s WHERE name=%s",
            (new_hash, user_name),
        )
        conn.commit()
        return True


def get_or_create_session(user_id: int, session_name: str) -> int:
    """Return id for the ``session_name`` of ``user_id``, creating if needed."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM sessions WHERE user_id=%s AND session_name=%s",
            (user_id, session_name),
        )
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute(
            "INSERT INTO sessions (user_id, session_name) VALUES (%s, %s) RETURNING id",
            (user_id, session_name),
        )
        session_id = cur.fetchone()[0]
        conn.commit()
        return session_id


def ensure_user(user_name: str) -> int:
    """Return ``user_id`` raising ``ValueError`` if user does not exist."""
    user_id = get_user_id(user_name)
    if user_id is None:
        raise ValueError("Usuário não encontrado")
    return user_id


def ensure_session(user_name: str, session_name: str) -> int:
    """Ensure session exists for ``user_name`` and return its id."""
    user_id = ensure_user(user_name)
    return get_or_create_session(user_id, session_name)


def save_record(user_name: str, session_name: str, subject: str, audio_path: str, original_text: str, translated_text: str):
    user_id = ensure_user(user_name)
    session_id = get_or_create_session(user_id, session_name)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO audio_records (session_id, subject, audio_path, original_text, translated_text)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (session_id, subject, audio_path, original_text, translated_text)
        )
        conn.commit()


def list_sessions(user_name: str) -> list[dict]:
    """Return all sessions for ``user_name`` with record counts."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT s.session_name, COUNT(ar.id) AS record_count
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN audio_records ar ON ar.session_id = s.id
            WHERE u.name = %s
            GROUP BY s.id
            ORDER BY s.created_at DESC
            """,
            (user_name,),
        )
        rows = cur.fetchall()
        return [
            {"session_name": r[0], "record_count": r[1]} for r in rows
        ]


def list_records(user_name: str, session_name: str) -> list[dict]:
    """Return all audio records for ``session_name`` of ``user_name``."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT ar.subject, ar.audio_path, ar.original_text, ar.translated_text, ar.created_at
            FROM audio_records ar
            JOIN sessions s ON ar.session_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE u.name = %s AND s.session_name = %s
            ORDER BY ar.created_at DESC
            """,
            (user_name, session_name),
        )
        rows = cur.fetchall()
        return [
            {
                "subject": r[0],
                "audio_path": r[1],
                "original_text": r[2],
                "translated_text": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]
