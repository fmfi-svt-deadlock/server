"""Helpers for working with the DB.

All of these expect to be passed a records.Database wrapping a psycopg2 connection.
"""

import collections
import logging
import select

log = logging.getLogger(__name__)


# TODO THIS IS NOT THREAD-SAFE! How to do a thread-safe transaction with a shared connection,
# anyway? psycopg2's cursors are thread-safe, but this doesn't make it through the layers of abstraction. Argh :-/
# class transaction:
#     """A context manager for a DB transaction.

#     Automatically commits at the end of the with body, or rollbacks if an exception was raised.
#     You can also explicitly call t.commit() and t.rollback() if you want to.
#     """
#     def __init__(self, db, ro=False):
#         self.db = db
#         self.ro = ro

#     def __enter__(self):
#         self.db.query('BEGIN TRANSACTION {}'.format('READ ONLY' if self.ro else 'READ WRITE'))
#         self._needs_commit = True
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         if self._needs_commit: self.db.query('ROLLBACK' if exc_type else 'COMMIT')
#         return False  # propagate exception if any

#     def commit(self):
#         """Commit the transaction right now."""
#         self.db.query('COMMIT')
#         self._needs_commit = False

#     def rollback(self):
#         """Rollback the transaction right now."""
#         self.db.query('ROLLBACK')
#         self._needs_commit = False


Notify = collections.namedtuple('Notify', ['channel', 'callback'])

def listen_for_notify(db, channels, callback, debounce_timeout=1):
    """Listen for Postgres's NOTIFY, debouncing/deduplicating notifications.

    debounce_timeout is in seconds.
    """
    for ch in channels: db.query('LISTEN {}'.format(ch))
    log.info('LISTEN on: {}'.format(', '.join(channels)))
    conn = db.db.connection.connection  # too many wrappers
    conn.commit()
    while True:
        select.select([conn], [], [])  # wait until we've gotten something
        while True:  # debounce
            conn.poll()  # poke psycopg2 to look at the socket
            if not conn.notifies: break
            if select.select([conn], [], [], debounce_timeout) == ([], [], []): break  # timeout, fw
        if not conn.notifies: continue
        notifies = {Notify(n.channel, n.payload) for n in conn.notifies}
        conn.notifies.clear()
        for n in notifies: callback(n)
