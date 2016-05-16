from datetime import date, time, datetime
import functools
import json

import cherrypy
import records


def m(orig, *over):
    """Return a new dict merged from the given ones. Last wins."""
    r = orig.copy()
    for d in over: r.update(d)
    return r


def header(key, value):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            cherrypy.response.headers[key] = value
            return f(*args, **kwargs)
        return wrapped
    return decorator


class _cpJSONEncoder(json.JSONEncoder):
    """A CherryPy-compatible JSON encoder that can encode a few extra types."""
    def default(self, obj):
        if isinstance(obj, (date, time, datetime)):
            return obj.isoformat()
        if isinstance(obj, memoryview):
            return obj.tobytes().decode(encoding='UTF-8')
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode(encoding='UTF-8')
        if isinstance(obj, records.Record):
            return obj.as_dict()
        else:
            return super().default(obj)

    def iterencode(self, value, *args, **kwargs):
        """Unlike normal iterencode, returns bytes, not string, for compatibility with CherryPy."""
        # Adapted from cherrypy/_cpcompat.py
        for chunk in super().iterencode(value, *args, **kwargs):
            yield chunk.encode("utf-8")

def json_handler(*args, **kwargs):
    """Streaming JSON encoder for CherryPy. It can handle a few extra types."""
    # Adapted from cherrypy/lib/jsontools.py
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return _cpJSONEncoder().iterencode(value)


@cherrypy.tools.json_in()
@cherrypy.tools.json_out(handler=json_handler)
class Resource:
    """An exposed RESTful resource that likes JSON and needs a DB connection."""
    exposed = True

    def __init__(self, db):
        self.db = db
