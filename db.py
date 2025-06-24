import os
import psycopg2
from psycopg2.extras import RealDictCursor
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


def save_record(user_name: str, subject: str, audio_path: str, original_text: str, translated_text: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO audio_records (user_name, subject, audio_path, original_text, translated_text)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_name, subject, audio_path, original_text, translated_text)
        )
        conn.commit()
