"""The controller ↔ server API -- the business logic.

This knows what should happen for a given request. See `protocol` for
the message format details.
"""

import base64
import logging

from common import cfiles

from . import handlers
from . import protocol

log = logging.getLogger(__name__)

def log_request(hdr, req):
    log.info('->{type} from {id} [{nonce}]'.format(
        type=req.msg_type.name, id=protocol.show_id(hdr.controller_id),
        nonce=protocol.show_nonce(hdr.nonce)))

def log_response(hdr, msg_type, status):
    log.info('<-{type} {status} to {id} [{nonce}]'.format(
        type=msg_type.name, status=status.name, id=protocol.show_id(hdr.controller_id),
        nonce=protocol.show_nonce(hdr.nonce)))

def log_bad_message(buf, e, maxlen):
    log.error('->BAD MSG: {arg} -- buf: [size {size}] {buf}'.format(
        arg=' '.join(e.args), size=len(buf),
        buf=base64.b64encode(buf[:maxlen]).decode('ascii')))


class API:
    def __init__(self, config, db):
        self.config = config
        self.db     = db
        self.cfiles = cfiles.ControllerFiles(self.config.controller_files_path)
        self.allowed_msg_types = { protocol.MsgType[x] for x in config.allowed_msg_types }

    def handle_packet(self, in_buf):
        try:
            request_header, request = protocol.parse_packet(protocol.Request, in_buf, self.get_key)
            log_request(request_header, request)
            handler = handlers.get_handler_for(request.msg_type, self.allowed_msg_types)
            result = handler(request_header.controller_id, request.data.val, api=self)
            if not result: return None
            status, response = result
            response_packet = protocol.make_response_packet_for(
                request_header, request.msg_type, status, response, get_key=self.get_key)
            log_response(response_packet.header, request.msg_type, status)
            return response_packet.pack()
        except protocol.BadMessageError as e:
            log_bad_message(in_buf, e, getattr(self.config, 'log_message_bytes', 1024))

    # TODO if protocol crypto and insides were better separated, this could just create a
    # {de,en}cryption black box and thereby avoid telling the key to anyone else.
    def get_key(self, id):
        """Loads the key for this controller from the DB."""
        rows = self.db.query('SELECT key FROM controller WHERE mac = :id',
                             id=protocol.show_id(id)).all()
        protocol.check(len(rows) == 1, 'unknown controller ID')
        return bytes(rows[0]['key'])
