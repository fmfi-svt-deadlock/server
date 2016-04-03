"""The controller ↔ server API -- the business logic.

This knows what should happen for a given request. See `controller_protocol` for
the message format details.
"""

from . import protocol
from .protocol import MsgType, ResponseStatus as Status

from structparse.types import Tail  # TODO remove

class API:
    def __init__(self, db_conn):
        self.db = db_conn

    def handle_packet(self, in_buf):
        try:
            request_header, request = protocol.parse_packet(protocol.Request, in_buf, get_key=self.get_key)
            status, response_data = self.process_request[request.msg_type](request_header.controller_id, request.data)  # TODO this will be rewritten
            self.log_message(request_header.controller_id, request, status)
            response_packet = protocol.make_response_packet_for(request_header, request.msg_type, status, response_data, get_key=self.get_key)
            return response_packet.pack()
        except protocol.BadMessageError as e:
            log_bad_message(buf, e)

    # TODO this table will be dynamic via handler registration -- pretend it doesn't exist
    process_request = {
        # TODO this should get data.isic_id, except that's not implemented yet and structparse needs unions and stuff
        MsgType.OPEN: (lambda id, data: ((Status.OK if data == Tail(b'Hello') else Status.ERR), None))
    }

    def get_key(self, id):
        """Loads the key for this controller from the DB."""
        rs = self.db.exec_sql('SELECT key FROM controller WHERE id = %s',
                              (protocol.id2str(id),), ret=True)
        protocol.check(len(rs) == 1, 'unknown controller ID')
        return bytes(rs[0]['key'])

    def log_message(self, controller_id, request, status):
        """TODO"""
        # print(utils.bytes2mac(controller_id), mtype.name, indata, '->', status.name)
        print(protocol.id2str(controller_id), request, '->', status.name)

    def log_bad_message(self, buf, e):
        """TODO"""
        raise e

assert set(protocol.MsgType) == set(API.process_request), 'Not all message types handled'
