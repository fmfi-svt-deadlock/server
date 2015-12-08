"""The UDP server that provides the API for the controllers."""

from . import controller_api
import socketserver

class MessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        """Handles a request from the controller."""
        in_packet, socket = self.request
        out_packet = controller_api.handle_packet(in_packet)
        if out_packet: socket.sendto(out_packet, self.client_address)

def serve(config):
    bind_addr = config.udp_host, config.udp_port
    server = socketserver.ThreadingUDPServer(bind_addr, MessageHandler)
    server.serve_forever()
