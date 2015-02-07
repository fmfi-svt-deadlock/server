"""Defines the REST API for CRUD and management."""

from . import db
import nacl.raw as nacl
import cherrypy

class MountPoint:
    """Represents a mount point, or path prefix, for attaching resources to."""

class Resource(MountPoint):
    """Represents a REST resource."""
    exposed = True

class Log(Resource):
    @cherrypy.tools.json_out()
    def GET(self, entries=100):
        return db.exec_sql('SELECT * FROM log ORDER BY time DESC LIMIT %s',
                           (entries,), ret=True)

class CRUDResource(Resource):
    """Represents a REST resource that exposes a DB table's CRUD methods."""
    def __init__(self, tbl, put_columns, get_columns, on_save=lambda x: x):
        assert(tbl.isidentifier())
        self.table       = tbl
        self.put_columns = put_columns
        self.get_columns = get_columns
        self.on_save     = on_save

    @cherrypy.tools.json_out()
    def GET(self, id=None):
        cols = list(self.get_columns)
        q = 'SELECT {} FROM {}'.format(','.join(cols), self.table)
        if id: q += ' WHERE id = %s'
        rs = db.exec_sql(q, (id,), ret=True)
        if id:
            if len(rs) < 1: raise cherrypy.HTTPError('404 Not Found')
            return rs[0]
        else: return rs

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, id):
        json = self.on_save(dict(cherrypy.request.json, id=id))
        print(json)
        cols, values, ps = [], [], []
        for c in self.put_columns:
            cols.append(c)
            values.append(json.get(c))
            ps.append('%s')
        q = 'INSERT INTO controller ({}) VALUES ({})'.format(','.join(cols),
                                                             ','.join(ps))
        try:
            db.exec_sql(q, values)
        except db.IntegrityError as e:
            raise cherrypy.HTTPError('400 Bad Request', e.pgerror) from e
        return { 'url': cherrypy.url() }

    # TODO POST

    def DELETE(self, id):
        db.exec_sql('DELETE FROM {} WHERE id = %s'.format(self.table), (id,))

################################################################################

api_root = MountPoint()
api_root.controller = CRUDResource('controller',
        get_columns={'id', 'ip', 'name'},
        put_columns={'id', 'ip', 'key', 'name'},
        on_save=lambda ctrl:
            dict(ctrl, key=nacl.randombytes(nacl.crypto_secretbox_KEYBYTES)))
api_root.log = Log()

################################################################################

cherrypy_conf = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    }
}
cherrypy.tree.mount(api_root, '/', cherrypy_conf)

def serve(config):
    cherrypy.config.update({'server.socket_port': config.http_port})
    cherrypy.engine.start()

def stop():
    cherrypy.engine.exit()
