CREATE TABLE IF NOT EXISTS audio_records (
    id SERIAL PRIMARY KEY,
    user_name TEXT NOT NULL,
    subject TEXT NOT NULL,
    audio_path TEXT NOT NULL,
    original_text TEXT,
    translated_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
