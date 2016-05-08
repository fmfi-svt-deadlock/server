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
    default_params = dict(
        limit=200,
    )

    def GET(self, **params):
        # TODO filtering
        params_keys = set(self.default_params).intersection(set(cherrypy.request.params))
        params = utils.m(self.default_params, cherrypy.request.params)
        return self.db.query('''
            SELECT a.id, a.time, p.name AS accesspoint, c.mac AS controller, card, allowed
            FROM accesslog a LEFT OUTER JOIN controller c ON a.controller = c.id
                 LEFT OUTER JOIN accesspoint p ON c.id = p.controller
            ORDER BY time DESC LIMIT :limit
            ''', **params).all()

class Status(ResourceWithDB):
    def GET(self):
        return self.db.query('''
            SELECT p.name, ip, t.name AS type, c.mac, last_seen, db_version, fw_version
            FROM accesspoint p
                 LEFT OUTER JOIN aptype t ON p.type = t.id
                 LEFT OUTER JOIN controller c ON p.controller = c.id
            ORDER BY type
            ''').all()

class AccessPoint(ResourceWithDB):
    def GET(self, id=None):
        return {'got id': id}

class Ruleset(ResourceWithDB):
    def GET(self, id=None):
        if not id:
            return self.db.query('SELECT name FROM ruleset').all()

        meta = self.db.query('SELECT name,mtime FROM ruleset WHERE id=:id', id=id).all()
        if not meta: raise cherrypy.NotFound
        rule = self.db.query(
            'SELECT ap.name AS aptype, r.priority, t.name AS time_spec, '
            'FROM rule r '
            '     JOIN ruleset s   ON r.ruleset = s.id '
            '     JOIN time_spec t ON r.time_spec = t.id '
            '     JOIN aptype ap   ON r.aptype = ap.id '
            'WHERE ruleset = :name', name=name).all(as_dict=True)

        rule = self.db.query(
            'SELECT aptype, r.priority, r.time_spec, expr, rkind'
            ' FROM rule r JOIN ruleset s ON r.ruleset = s.id'
            ' WHERE s.name = :name', name=name).all()
        rule = self.db.query(
            'SELECT aptype, r.priority, r.time_spec, expr, rkind'
            ' FROM rule r JOIN ruleset s ON r.ruleset = s.id'
            ' WHERE s.name = :name', name=name).all()

        time_spec = {'mrkva': 128}
        identity_expr = {'mrkva': 256}
        return dict(rule=rule, time_spec=time_spec, identity_expr=identity_expr)
