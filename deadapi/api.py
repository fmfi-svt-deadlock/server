"""TODO"""
import contextlib
import logging
import queue
import select
import threading
import time

import cherrypy

from . import utils

log = logging.getLogger(__name__)

@cherrypy.tools.json_in()
@cherrypy.tools.json_out(handler=utils.json_handler)
class Resource:
    """An exposed RESTful resource that needs a DB connection to be happy."""
    exposed = True

    def __init__(self, db):
        self.db = db

def show_card(m):
    return m.tobytes().encode('')

class AccessLog(Resource):
    def GET(self):
        return self.db.query(
            'SELECT a.id, a.time, p.name AS accesspoint, c.mac AS controller, card, allowed '
            'FROM accesslog a LEFT OUTER JOIN controller c ON a.controller_id = c.id '
            '     LEFT OUTER JOIN accesspoint p ON c.id = p.controller_id '
            'ORDER BY time').all(as_dict=True)


# TODO send diff! totally possible! :D
class Events:
    EVENTS = {  # notify channel: event name
        'accesslog_change': 'accesslog_update',
    }
    DEBOUNCE_TIMEOUT = 2  # seconds

    def __init__(self, db):
        self.log = logging.getLogger(self.__class__.__qualname__)
        self.db = db
        self.event_queues = set()
        self.event_queues_guard = threading.Lock()
        threading.Thread(target=self.listen, daemon=True).start()

    # TODO the same as offlinedb -- refactor
    def listen(self):
        self.db.db.execution_options(isolation_level='AUTOCOMMIT')
        log = logging.getLogger(self.__class__.__qualname__)
        for ch in self.EVENTS:
            self.log.info('LISTEN {}'.format(ch))
            self.db.query('LISTEN {}'.format(ch))
        conn = self.db.db.connection.connection  # too many wrappers
        while True:
            select.select([conn], [], [])  # wait until we've gotten something
            # debounce
            while True:
                conn.poll()  # poke psycopg2 to look at the socket
                if select.select([conn], [], [], self.DEBOUNCE_TIMEOUT) == ([], [], []):
                    break
            log.info('NOTIFY received')
            events = set()
            while conn.notifies:
                events.add(self.EVENTS[conn.notifies.pop().channel])
            for e in events:
                with self.event_queues_guard:
                    evts = self.event_queues.copy()

                for q in evts:
                    print('queued', e)
                    try:
                        q.put_nowait(e)
                    except queue.QueueFull:
                        self.log.exception('event queue full, closing')

    # TODO awful memory leak! when threads die, I can't detect it and therefore nobody cleans up
    # event_queues!!!
    @contextlib.contextmanager
    def get_queue(self):
        q = queue.Queue(maxsize=20)  # small size to avoid running out of memory on stale stuff
        with self.event_queues_guard:
            self.event_queues.add(q)
        self.log.debug('added queue')
        yield q
        with self.event_queues_guard:
            self.event_queues.discard(q)
        self.log.debug('removed queue')
        self.log.debug('event_queues: {}'.format(self.event_queues))

class EventSource:
    exposed = True
    _cp_config = {'response.stream': True}

    def __init__(self, db):
        self.events = Events(db)
        self.log = logging.getLogger(self.__class__.__qualname__)

    def GET(self):
        cherrypy.response.headers['Content-Type'] = 'text/event-stream'

        def stream():
            yield '\n'  # push headers
            with self.events.get_queue() as q:
                while True:
                    try:
                        e = q.get(timeout=10)
                        self.log.debug('sending to client {}: {}'.format(
                            cherrypy.request.remote.ip, e))
                        yield 'data: {}\n\n'.format(e)
                    except queue.Empty:
                        yield '\n'  # force cherrypy to look at this conn by writing to its socket
        return stream()


class Root:
    exposed = True

    def __init__(self, db):
        self.accesslog = AccessLog(db)
        self.events    = EventSource(db)

cpconfig = {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}
