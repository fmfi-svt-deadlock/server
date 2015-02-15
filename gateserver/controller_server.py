"""The UDP server that provides the API for the controllers."""

from . import controller_api
import socketserver

class MessageHandler(socketserver.BaseRequestHandler):
    """Handles a message from the controller.

    Behaves according to
    https://github.com/fmfi-svt/gate/wiki/Controller-%E2%86%94-Server-Protocol .
    """

    def handle(self):
        indata, socket = self.request
        outdata = controller_api.handle_request(indata)
        socket.sendto(outdata, self.client_address)

def serve(config):
    bind_addr = config.udp_host, config.udp_port
    server = socketserver.ThreadingUDPServer(bind_addr, MessageHandler)
    server.serve_forever()
