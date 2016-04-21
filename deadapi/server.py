import os
import sys

import cherrypy

import config
from . import api

def serve(config):
    cherrypy.config.update({
        'server.socket_host': config.http_host,
        'server.socket_port': config.http_port,
        'tools.proxy.on': True,
        'tools.proxy.local': 'Host',  # which header to look at for the local address
    })
    cherrypy.quickstart(api.Root(), '/', api.cpconfig)
