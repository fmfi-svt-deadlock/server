"""The UDP server that provides the API for the controllers."""

from . import controller_api
import socketserver

class MessageHandler(socketserver.BaseRequestHandler):
    """Handles a message from the controller."""

    def handle(self):
        in_packet, socket = self.request
        out_packet = controller_api.handle_request(in_packet)
        socket.sendto(out_packet, self.client_address)

def serve(config):
    bind_addr = config.udp_host, config.udp_port
    server = socketserver.ThreadingUDPServer(bind_addr, MessageHandler)
    server.serve_forever()
