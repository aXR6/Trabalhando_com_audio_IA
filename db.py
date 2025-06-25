import os
import psycopg2
from dotenv import load_dotenv

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


def get_or_create_user(user_name: str) -> int:
    """Return the id for ``user_name``, creating the user if needed."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE name=%s", (user_name,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO users (name) VALUES (%s) RETURNING id", (user_name,))
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id


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


def save_record(user_name: str, session_name: str, subject: str, audio_path: str, original_text: str, translated_text: str):
    user_id = get_or_create_user(user_name)
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
