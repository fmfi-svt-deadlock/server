"""Translates Postgres NOTIFY to HTTP Eventsource."""
import contextlib
import logging
import queue
import threading

import cherrypy

from common.utils.db import listen_for_notify

from .utils import header

log = logging.getLogger(__name__)

# TODO send diff! totally possible! :D
class Events:
    """Fans out notifies into all queues gotten from `self.get_queue`.

    Translates event names according to the given channels map.
    """
    DEBOUNCE_TIMEOUT = 2  # seconds

    def __init__(self, db, channels_map):
        """channels_map: dict of channel_name: event_name"""
        self.db = db
        self.EVENTS = channels_map
        self.event_queues = set()
        self.event_queues_guard = threading.Lock()
        threading.Thread(target=self.listen, daemon=True).start()

    # TODO for some reason cherrypy doesn't call close and therefore nobody cleans up event_queues!
    # for now workaround: small queue size, delete on full in forward_notify
    @contextlib.contextmanager
    def get_queue(self):
        q = queue.Queue(maxsize=20)  # small size to avoid running out of memory on stale stuff
        with self.event_queues_guard: self.event_queues.add(q)
        yield q
        with self.event_queues_guard: self.event_queues.discard(q)

    def forward_notify(self, notify):
        e = self.EVENTS[notify.channel]
        with self.event_queues_guard:
            queues = self.event_queues.copy()
        log.debug('sending {} to {} active event queues'.format(e, len(self.event_queues)))
        for q in queues:
            try:
                q.put_nowait(e)
            except queue.Full:
                with self.event_queues_guard: self.event_queues.discard(q)

    def listen(self):
        listen_for_notify(self.db, self.EVENTS, self.forward_notify)

class EventSource:
    """Translates Postgres NOTIFY to HTTP Eventsource."""
    exposed = True
    _cp_config = {'response.stream': True}

    def __init__(self, db, channels_map):
        """channels_map: dict of channel_name: event_name"""
        self.events = Events(db, channels_map)

    @header('Content-Type',      'text/event-stream')
    @header('Cache-Control',     'no-cache')
    @header('X-Accel-Buffering', 'no')  # tell proxies not to buffer this
    def GET(self):
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
