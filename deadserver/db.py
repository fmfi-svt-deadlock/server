"""Holds the (global) connection to the DB."""
# TODO maybe use a connection pool one beautiful day

import psycopg2
from psycopg2.extras import RealDictCursor  # results as dict instead of tuple

class Connection:
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        self.conn.autocommit = True

    def exec_sql(self, query, args=(), ret=False):
        """Executes the query, returning the result as a list if `ret`."""
        with self.conn.cursor() as cur:
            cur.execute(query, args)
            if ret: return cur.fetchall()

# thrown when constraints aren't satisfied
IntegrityError = psycopg2.IntegrityError
