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
from common.cfiles import filetypes
from common.utils.db import listen_for_notify
from deadserver import protocol

DEFAULT_NUM_THREADS = 8
WAIT_BEFORE_REBUILD = 5  # seconds; wait for the DB to settle, to avoid useless rebuilds

# TODO one day take specific actions depending on which one instead of rebuilding everything
NOTIFY_CHANNELS = ['identity_expr_change', 'rule_change', 'controller_change']

log = logging.getLogger(__name__)
db  = records.Database(config.db_url)
cf  = cfiles.ControllerFiles(config.controller_files_path)

def worker(q):
    while True:
        # TODO Adam should figure out what he wants to do here
        x = q.get()
        log.debug('would rebuild because of {}'.format(x))

def start(config):
    q = queue.Queue()
    nthreads = getattr(config, 'offlinedb_num_worker_threads', DEFAULT_NUM_THREADS)
    for _ in range(nthreads): threading.Thread(target=worker, args=[q]).start()
    log.info('{} worker threads created'.format(nthreads))

    def rebuild(notify):
        # TODO
        q.put(notify)

    listen_for_notify(db, NOTIFY_CHANNELS, rebuild, WAIT_BEFORE_REBUILD)
