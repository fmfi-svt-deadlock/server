import logging

import cherrypy

from . import utils

log = logging.getLogger(__name__)

@cherrypy.tools.json_in()
@cherrypy.tools.json_out(handler=utils.json_handler)
class Resource:
    """An exposed RESTful resource that likes JSON."""
    exposed = True

class ResourceWithDB(Resource):
    """An exposed RESTful resource that needs a DB connection to be happy."""
    def __init__(self, db):
        self.db = db


class AccessLog(ResourceWithDB):
    def GET(self):
        return self.db.query(
            'SELECT a.id, a.time, p.name AS accesspoint, c.mac AS controller, card, allowed'
            ' FROM accesslog a LEFT OUTER JOIN controller c ON a.controller_id = c.id'
            '     LEFT OUTER JOIN accesspoint p ON c.id = p.controller_id'
            ' ORDER BY time DESC LIMIT 100').all()

class Status(ResourceWithDB):
    def GET(self):
        return self.db.query(
            'SELECT p.name AS name, ip, t.name AS type, c.mac AS controller,'
            '       last_seen, db_version, fw_version'
            ' FROM accesspoint p LEFT OUTER JOIN aptype t ON p.type = t.id'
            '       LEFT OUTER JOIN controller c ON p.controller_id = c.id'
            ' ORDER BY type').all()

class AccessPoint(ResourceWithDB):
    def GET(self, name=None):
        return {'got name': name}

class Ruleset(ResourceWithDB):
    def GET(self, name=None):
        return {'got name': name}
