from __future__ import annotations
from contextlib import contextmanager
from typing import Mapping, Any
import json
from decimal import Decimal
from datetime import datetime, date
import psycopg
from psycopg.rows import dict_row
from jakan.common.config import load_config

@contextmanager
def get_conn():
    cfg = load_config()
    conn = psycopg.connect(
        host=cfg.host, port=cfg.port, dbname=cfg.db,
        user=cfg.user, password=cfg.password, row_factory=dict_row
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def run_sql_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

def json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value

def insert_rows(table: str, rows: list[Mapping[str, Any]]) -> int:
    if not rows:
        return 0
    columns = list(rows[0].keys())
    placeholders = ", ".join(["%s"] * len(columns))
    values = []
    for row in rows:
        converted = []
        for col in columns:
            value = row.get(col)
            if isinstance(value, (dict, list)):
                converted.append(json.dumps(value, default=json_safe, ensure_ascii=False))
            else:
                converted.append(value)
        values.append(converted)
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, values)
    return len(rows)

def fetch_all(sql: str, params: tuple | None = None) -> list[dict]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())
