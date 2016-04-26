from datetime import datetime
import json

import cherrypy

def m(d1, d2):
    """Return a new dict merged from the given ones. Last wins."""
    r = d1.copy()
    r.update(d2)
    return r


class _cpJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, memoryview):
            return obj.tobytes().decode(encoding='UTF-8')
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode(encoding='UTF-8')
        else:
            return super().default(obj)

    def iterencode(self, value, *args, **kwargs):
        # Adapted from cherrypy/_cpcompat.py
        for chunk in super().iterencode(value, *args, **kwargs):
            yield chunk.encode("utf-8")

_json_encoder = _cpJSONEncoder()

def json_handler(*args, **kwargs):
    """Streaming JSON encoder for CherryPy. It can handle a few extra types."""
    # Adapted from cherrypy/lib/jsontools.py
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return _json_encoder.iterencode(value)
