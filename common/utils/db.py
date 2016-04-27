"""Helpers for working with the DB.

All of these expect to be passed a records.Database wrapping a psycopg2 connection.
"""

import collections
import contextlib
import logging
import select

log = logging.getLogger(__name__)

@contextlib.contextmanager
def transaction(db, ro=False):
    db.query('BEGIN TRANSACTION {}'.format('READ ONLY' if ro else 'READ WRITE'))
    yield lambda: db.query('COMMIT')
    db.query('COMMIT' if ro else 'ROLLBACK')


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
