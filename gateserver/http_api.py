"""Defines the REST API for CRUD and management."""

from .models import Controller  # TODO ...and others, once they exist

import cherrypy
import psycopg2
import config

class RestMixin():
    """Mixin to expose the given model via REST."""

    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, id=None):
        r = self.get(id)
        if r == None: raise cherrypy.NotFound()
        else: return r

    @cherrypy.tools.json_in()
    def PUT(self, id):
        try:
            return self.create(id, **cherrypy.request.json)
        except psycopg2.IntegrityError as e:
            raise cherrypy.HTTPError("409 Conflict", e.pgerror)

    def DELETE(self, id):
        self.delete(id)

def expose_at(path):
    def mount(cls):
        cherrypy.tree.mount(cls(), path, {'/': cherrypy_model_endpoint_conf})
    return mount

################################################################################

cherrypy_model_endpoint_conf = {
    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
}

@expose_at('/controller')
class ControllerAPI(RestMixin, Controller): pass

################################################################################

def serve(config):
    cherrypy.config.update({'server.socket_port': config['port'],})
    cherrypy.engine.start()
