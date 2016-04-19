"""Holds the (global) connection to the DB."""
# TODO maybe use a connection pool one beautiful day

import psycopg2
from psycopg2.extras import RealDictCursor  # results as dict instead of tuple

conn = None

def connect(db_url):
    global conn
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    conn.autocommit = True

def exec_sql(query, args=(), ret=False):
    """Execute the query, returning the result as a list if `ret` is set."""
    with conn.cursor() as cur:
        cur.execute(query, args)
        if ret: return cur.fetchall()

# thrown when constraints aren't satisfied
IntegrityError = psycopg2.IntegrityError
