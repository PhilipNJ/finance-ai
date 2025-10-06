import sqlite3
import datetime as dt
from typing import List, Tuple
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / 'data' / 'finance.db'

SCHEMA = {
    'documents': (
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            uploaded_at TEXT NOT NULL
        )
        """
    ),
    'transactions': (
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            date TEXT,
            amount REAL,
            description TEXT,
            category TEXT,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )
        """
    ),
    'mem_labels': (
        """
        CREATE TABLE IF NOT EXISTS mem_labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            category TEXT NOT NULL
        )
        """
    ),
}


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    con = get_conn()
    try:
        cur = con.cursor()
        for ddl in SCHEMA.values():
            cur.execute(ddl)
        con.commit()
    finally:
        con.close()


def insert_document(filename: str) -> int:
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO documents (filename, uploaded_at) VALUES (?, ?)",
            (filename, dt.datetime.utcnow().isoformat()),
        )
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def insert_transactions(document_id: int, rows: List[Tuple[str, float, str, str]]):
    con = get_conn()
    try:
        cur = con.cursor()
        cur.executemany(
            "INSERT INTO transactions (document_id, date, amount, description, category) VALUES (?, ?, ?, ?, ?)",
            [(document_id, d, a, desc, cat) for d, a, desc, cat in rows],
        )
        con.commit()
    finally:
        con.close()


def read_transactions_df():
    import pandas as pd
    con = get_conn()
    try:
        df = pd.read_sql_query(
            "SELECT t.id, t.document_id, t.date, t.amount, t.description, t.category, d.filename "
            "FROM transactions t LEFT JOIN documents d ON t.document_id = d.id ORDER BY t.date",
            con,
        )
        return df
    finally:
        con.close()


def upsert_mem_label(keyword: str, category: str):
    keyword = keyword.strip().lower()
    if not keyword:
        return
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO mem_labels (keyword, category) VALUES (?, ?)", (keyword, category)
        )
        con.commit()
    finally:
        con.close()


def get_mem_labels() -> List[Tuple[str, str]]:
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute("SELECT keyword, category FROM mem_labels")
        return cur.fetchall()
    finally:
        con.close()
