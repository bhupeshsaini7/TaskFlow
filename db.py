"""Small helpers for talking to MySQL.

Every query uses %s placeholders plus a separate params tuple, so user input
is never pasted into the SQL text. This prevents SQL injection.
"""
import mysql.connector

from config import Config


def get_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        connection_timeout=5,
    )


def fetch_all(sql, params=()):
    """Run a SELECT and return a list of dictionaries."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def fetch_one(sql, params=()):
    """Run a SELECT and return one dictionary (or None if nothing matches)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        row = cursor.fetchone()
        cursor.close()
        return row
    finally:
        conn.close()


def execute(sql, params=()):
    """Run an INSERT / UPDATE / DELETE and save (commit) the change."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
    finally:
        conn.close()