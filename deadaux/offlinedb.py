"""Listens for rule changes and prepares offlinedb files for controllers."""

# TODO: right now this rebuilds everything, but it would be easy to make this incremental. Do it one
# day. (Needs also incremental DB update in `sql/01-materialize-rules.sql`.)

import logging
import queue
import select
import threading
import time

import psycopg2
import records

import config
from common import cfiles
from common import filetypes
from deadserver import protocol

DEFAULT_NUM_THREADS = 8
WAIT_BEFORE_REBUILD = 5  # seconds; wait for the DB to settle, to avoid useless rebuilds

# TODO one day take specific actions depending on which one instead of rebuilding everything
NOTIFY_CHANNELS = { 'identity_expr_change', 'rule_change', 'controller_change' }

log = logging.getLogger(__name__)
db  = records.Database(config.db_url); db.db.execution_options(isolation_level='AUTOCOMMIT')
cf  = cfiles.ControllerFiles(config.controller_files_path)

def listen_for_notify(channels, callback):
    for ch in NOTIFY_CHANNELS: db.query('LISTEN {}'.format(ch))
    conn = db.db.connection.connection  # too many wrappers
    while True:
        select.select([conn],[],[])  # wait until we've gotten something
        # debounce
        while True:
            conn.poll()  # poke psycopg2 to look at the socket
            if select.select([conn],[],[], WAIT_BEFORE_REBUILD) == ([],[],[]):  break  # timeout
        log.info("NOTIFY received")
        callback(conn.notifies)
        conn.notifies.clear()

def worker(q):
    while True:
        ...

def start(config):
    q = queue.Queue()
    nthreads = getattr(config, 'offlinedb_num_worker_threads', DEFAULT_NUM_THREADS)
    for _ in range(nthreads): threading.Thread(target=worker, args=[q]).start()
    log.info('{} worker threads created'.format(nthreads))

    def rebuild(notifies):
        # TODO
        while notifies: print(notifies.pop())

    listen_for_notify(NOTIFY_CHANNELS, rebuild)



# def create_db_for(mac):
#     version = int(time.time())  # fits into uint64
#     log.info("DB for {}, v{}: starting...".format(mac, version))
#     filename = filetypes.filename(ftype=filetypes.FileType.DB, version=version)
#     with cf.open(filename, protocol.str2id(mac), 'wb') as f:
#         f.write(bytes(str(time.time()), 'utf8'))
#         f.write(b'\n\nmrkva v zime\n')
#     log.info("DB for {}, v{}: done".format(mac, version))

#        for row in db.query('SELECT mac FROM controller c JOIN door d ON c.id = d.controller_id'): q.put(row.mac)
#        q.join()
#        log.info('all done, going to sleep')
