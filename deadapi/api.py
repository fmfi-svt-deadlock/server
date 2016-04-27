"""The HTTP API to the Deadlock server. Defines API endpoints / HTTP resource mountpoints."""

import cherrypy

from . import events
from . import resources

class Root:
    exposed = True

    def __init__(self, db):
        self.ruleset     = resources.Ruleset(db)
        self.accesspoint = resources.AccessPoint(db)
        self.status      = resources.Status(db)
        self.accesslog   = resources.AccessLog(db)
        self.events      = events.EventSource(db, {  # notify channel: event name
            'accesslog_change': 'accesslog_update',
            'status_change':    'status_update',
        })

cpconfig = {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}
