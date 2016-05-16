"""The HTTP API to the Deadlock server. Defines API endpoints / HTTP resource mountpoints."""

import cherrypy

from . import events
from . import resources

# Note: the ruleset semantics means atomic flipping of rulesets is guaranteed, but nothing else
# flips atomically. I believe that's OK.

class Root:
    exposed = True

    def __init__(self, db):
        self.accesslog     = resources.AccessLog(db)     # TODO filtering
        self.status        = resources.Status(db)
        self.controller    = resources.Controller(db)    # TODO figure out provisioning
        self.accesspoint   = resources.AccessPoint(db)   # TODO PUT, POST
        self.ruleset       = resources.Ruleset(db)       # TODO PUT, POST
        self.identity_expr = resources.IdentityExpr(db)  # TODO PUT, POST
        self.events        = events.EventSource(db, {
            'accesslog_change': 'accesslog_update',
            'status_change':    'status_update',
        })

cpconfig = {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}
