import cherrypy
import sqlalchemy.exc
import nacl.secret
import nacl.utils

from .. import utils

class Controller(utils.Resource):
    def GET(self):
        """List all controllers."""
        return self.db.query('''
            SELECT c.id, p.id AS ap_id, p.name AS ap, last_seen
            FROM controller c LEFT OUTER JOIN accesspoint p ON p.controller = c.id
            ORDER BY last_seen
            ''').all()

    def POST(self, **params):
        """Add a controller, generating a key."""
        key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
        try:
            self.db.query('INSERT INTO controller (key) VALUES (:key)', key=key)
            new = self.db.query('SELECT id FROM controller WHERE key = :key', key=key)[0]['id']
            new_url = '{}/{}'.format(cherrypy.request.path_info, new)
            cherrypy.response.status = "201 Created"
            cherrypy.response.headers['Location'] = new_url
            return {'id': new, 'url': new_url}
        except sqlalchemy.exc.IntegrityError as e:
            cherrypy.response.status = "409 Conflict"
            return {'error': e.args[0]}
