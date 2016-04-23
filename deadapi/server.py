import os
import sys

import cherrypy
import records

import config
from . import api

def kill_default_logging():
    cherrypy.log.error_file = cherrypy.log.access_file = ''
    cherrypy.log.screen = False

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)

def serve(config):
    cherrypy.config.update({
        'server.socket_host': config.http_host,
        'server.socket_port': config.http_port,
        'tools.proxy.on': True,
        'tools.proxy.local': 'Host',  # which header to look at for the local address
        'tools.CORS.on': True,  # for now
    })
    cherrypy.quickstart(api.Root(records.Database(config.db_url)), '/', api.cpconfig)
