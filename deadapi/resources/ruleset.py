import cherrypy

from .. import utils

class Ruleset(utils.Resource):
    # TODO POST, PUT
    def GET(self, id=None):
        if not id:
            return self.db.query('SELECT id, name, mtime FROM ruleset').all()

        meta = self.db.query('SELECT id, name, mtime FROM ruleset WHERE id = :id', id=id).all()
        if not meta: raise cherrypy.NotFound

        rule = self.db.query('''
            SELECT id, priority, aptype, time_spec, expr, result
            FROM rule WHERE ruleset = :id''', id=id).all()
        time_spec = self.db.query(
            '''
            SELECT t.id, t.name, time_from, time_to, weekday_mask, date_from, date_to
            FROM time_spec t JOIN rule r ON t.id = r.time_spec WHERE r.ruleset = :id''',
            id=id).all()
        return dict(meta=meta[0], rule=rule, time_spec=time_spec)
