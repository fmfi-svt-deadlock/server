"""The UDP server that provides the API for the controllers."""

#from . import controller_api
import socketserver
import logging

log = logging.getLogger('server')

class MessageHandler(socketserver.BaseRequestHandler):
    """Handles a message from the controller.

    Behaves according to
    https://github.com/fmfi-svt/gate/wiki/Controller-%E2%86%94-Server-Protocol .
    """

    def handle(self):
        data, socket = self.request
        socket.sendto(data, self.client_address)
        log.info(data, extra=dict(ip=self.client_address[0], status='OK'))

def serve(config):
    bind_addr = '0.0.0.0', config.udp_port
    server = socketserver.ThreadingUDPServer(bind_addr, MessageHandler)
    server.serve_forever()
