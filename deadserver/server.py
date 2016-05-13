"""The UDP server that handles controller messages.

Wraps `messages.MessageHandler` by hanging it onto a socket.
"""

import socketserver

import records

from . import messages

def serve(config):
    db = records.Database(config.db_url)
    db.db.execution_options(isolation_level='AUTOCOMMIT')

    handler = messages.MessageHandler(messages.Context(config=config, db=db))

    class MessageHandler(socketserver.BaseRequestHandler):
        def handle(self):
            """Handles a request from the controller."""
            in_packet, socket = self.request
            out_packet = handler.handle(in_packet)
            if out_packet: socket.sendto(out_packet, self.client_address)

    server = socketserver.ThreadingUDPServer((config.host, config.port), MessageHandler)
    server.max_packet_size = 65536
    server.serve_forever()
