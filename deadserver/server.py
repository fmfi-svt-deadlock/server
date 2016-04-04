"""The UDP server that handles controller messages.

This is not concerned with the protocol details, it only knows how to receive
requests and send responses, and passes stuff to `controller_api`.
"""

import functools
import socketserver

import records

from . import api

class MessageHandler(socketserver.BaseRequestHandler):
    def __init__(self, api, *args, **kwargs):
        self.api = api
        super().__init__(*args, **kwargs)

    def handle(self):
        """Handles a request from the controller."""
        in_packet, socket = self.request
        out_packet = self.api.handle_packet(in_packet)
        if out_packet: socket.sendto(out_packet, self.client_address)

class DeadServer:
    def __init__(self, config):
        self.config  = config
        self.db      = records.Database(self.config.db_url)
        self.handler = functools.partial(MessageHandler, api.API(db=self.db))

        bind_addr = self.config.udp_host, self.config.udp_port
        self.server = socketserver.ThreadingUDPServer(bind_addr, self.handler)

    def serve(self):
        self.server.serve_forever()
