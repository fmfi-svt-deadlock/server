"""The UDP server that handles controller messages.

This only knows how to receive requests and send responses -- it is just a thin wrapper around
`api.API` and it is not concerned with the protocol details.

"""

import socketserver

import records

from . import api

def serve(config):
    db = records.Database(config.db_url)
    db.db.execution_options(isolation_level='AUTOCOMMIT')

    app = api.API(config=config, db=db)

    class MessageHandler(socketserver.BaseRequestHandler):
        def handle(self):
            """Handles a request from the controller."""
            in_packet, socket = self.request
            out_packet = app.handle_packet(in_packet)
            if out_packet: socket.sendto(out_packet, self.client_address)

    server = socketserver.ThreadingUDPServer((config.host, config.port), MessageHandler)
    server.serve_forever()
