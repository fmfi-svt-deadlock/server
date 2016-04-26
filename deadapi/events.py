import contextlib
import logging
import queue
import select
import threading

import cherrypy

log = logging.getLogger(__name__)

# TODO send diff! totally possible! :D
class Events:
    DEBOUNCE_TIMEOUT = 2  # seconds

    def __init__(self, db, channels_map):
        self.db = db
        self.EVENTS = channels_map
        self.event_queues = set()
        self.event_queues_guard = threading.Lock()
        threading.Thread(target=self.listen, daemon=True).start()

    # TODO the same as offlinedb -- refactor
    def listen(self):
        self.db.db.execution_options(isolation_level='AUTOCOMMIT')
        for ch in self.EVENTS:
            log.info('LISTEN {}'.format(ch))
            self.db.query('LISTEN {}'.format(ch))
        conn = self.db.db.connection.connection  # too many wrappers
        while True:
            select.select([conn], [], [])  # wait until we've gotten something
            # debounce
            while True:
                conn.poll()  # poke psycopg2 to look at the socket
                if select.select([conn], [], [], self.DEBOUNCE_TIMEOUT) == ([], [], []):
                    break
            if not conn.notifies: continue
            events = set()
            while conn.notifies:
                events.add(self.EVENTS[conn.notifies.pop().channel])
            log.info('NOTIFY received for {}'.format(', '.join(events)))
            for e in events:
                with self.event_queues_guard:
                    queues = self.event_queues.copy()
                log.debug('sending {} to {} active event queues'.format(e, len(self.event_queues)))
                for q in queues:
                    try:
                        q.put_nowait(e)
                    except queue.Full:
                        with self.event_queues_guard:
                            self.event_queues.discard(q)

    # TODO awful memory leak! for some reason cherrypy doesn't call close and therefore nobody
    # cleans up event_queues!!!
    # for now workaround: small queue size, delete on full
    @contextlib.contextmanager
    def get_queue(self):
        q = queue.Queue(maxsize=20)  # small size to avoid running out of memory on stale stuff
        with self.event_queues_guard:
            self.event_queues.add(q)
        yield q
        with self.event_queues_guard:
            self.event_queues.discard(q)

class EventSource:
    exposed = True
    _cp_config = {'response.stream': True}

    def __init__(self, db, channels_map):
        self.events = Events(db, channels_map)

    def GET(self):
        cherrypy.response.headers['Content-Type']  = 'text/event-stream'
        cherrypy.response.headers['Cache-Control'] = 'no-cache'
        cherrypy.response.headers['X-Accel-Buffering'] = 'no'

        def stream():
            yield '\n'  # push headers
            with self.events.get_queue() as q:
                while True:
                    try:
                        e = q.get(timeout=10)
                        log.debug('sending to client {}: {}'.format(
                            cherrypy.request.remote.ip, e))
                        yield 'data: {}\n\n'.format(e)
                    except queue.Empty:
                        yield '\n'  # force cherrypy to look at this conn by writing to its socket
        return stream()
