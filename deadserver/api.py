"""The controller ↔ server API -- the business logic.

This knows what should happen for a given request. See `controller_protocol` for
the message format details.
"""

from . import handlers
from . import protocol

class API:
    def __init__(self, config, db):
        self.config = config
        self.db     = db

    def handle_packet(self, in_buf):
        try:
            request_header, request = protocol.parse_packet(protocol.Request, in_buf, self.get_key)
            handler = handlers.get_handler_for(request.msg_type)
            status, response = handler(request_header.controller_id, request.data.val, api=self)
            self.log_message(request_header.controller_id, request, status)
            response_packet = protocol.make_response_packet_for(request_header, request.msg_type,
                status, response, get_key=self.get_key)
            return response_packet.pack()
        except protocol.BadMessageError as e:
            self.log_bad_message(in_buf, e)

    # TODO if protocol crypto and insides were better separated, this could just create a
    # {de,en}cryption black box and thereby avoid telling the key to anyone else.
    def get_key(self, id):
        """Loads the key for this controller from the DB."""
        rows = self.db.query('SELECT key FROM controller WHERE id = :id',
                             id=protocol.id2str(id)).all()
        protocol.check(len(rows) == 1, 'unknown controller ID')
        return bytes(rows[0]['key'])

    def log_message(self, controller_id, request, status):
        """TODO"""
        # print(utils.bytes2mac(controller_id), mtype.name, indata, '->', status.name)
        print(protocol.id2str(controller_id), request, '->', status.name)

    def log_bad_message(self, buf, e):
        """TODO"""
        raise e
