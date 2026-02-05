import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "switchlang.db"

def init_db():
    """Initialize the SQLite database and create table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            src_lang TEXT,
            tgt_lang TEXT,
            source_text TEXT,
            user_input TEXT,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_result(src_lang, tgt_lang, source_text, user_input, feedback):
    """Save a single practice result to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO study_history (timestamp, src_lang, tgt_lang, source_text, user_input, feedback)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now(), src_lang, tgt_lang, source_text, user_input, feedback))
    conn.commit()
    conn.close()

def get_history():
    """Retrieve all history as a pandas DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM study_history ORDER BY timestamp DESC", conn)
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()