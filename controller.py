"""Quick & dirty client (i.e. the controller end), used for manual testing of the server."""

from binascii import hexlify
import ipaddress
import logging
import random
import socket
import sys

from records import Database

import config
from common import types
from deadserver.protocol import utils, wirefmt
from deadserver.protocol.constants import MsgType, ResponseStatus

log = logging.getLogger(__name__)

class DumbController:
    """An implementation of the controller. Can only send given messages."""
    def __init__(self, conf, crypto_box):
        self.conf = conf
        self.conf.CONFIG_KEY = '(not needed -- using CryptoBox)'
        self.id = conf.CONFIG_ID
        self.crypto_box = lambda _: crypto_box  # lambda because wirefmt accepts functions

    def request(self, msg_type, data, timeout=None):
        req_buf = wirefmt.write_request(msg_type, data)
        out_envelope = wirefmt.new_envelope(self.id)
        out_buf = wirefmt.close_envelope(out_envelope, req_buf, self.crypto_box)
        in_buf = self._send(out_buf, timeout)
        re_envelope, response_buf = wirefmt.open_envelope(in_buf, self.crypto_box)
        utils.check(re_envelope.NONCE == wirefmt.re_nonce(out_envelope.NONCE),
                    'Got OT response nonce: {} (expected {})'.format(
                        re_envelope.NONCE, wirefmt.re_nonce(out_envelope.NONCE)))
        re_msg_type, status, re_data = wirefmt.read_response(response_buf)
        utils.check(re_msg_type == msg_type,
                    'Got OT response type: {} (expected {})'.format(
                        re_msg_type.name, msg_type.name))
        return status, re_data

    def _send(self, buf, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        host = random.choice(self.conf.CONFIG_SERVERS)
        sock.sendto(buf, (host.exploded, self.conf.CONFIG_SERVER_PORT))
        return sock.recv(64000)

if __name__ == '__main__':
    cid, msg_type = int(sys.argv[1]), sys.argv[2]
    if len(sys.argv) >= 4 and sys.argv[3] == '-v':  # TODO argparse or click or something
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(levelname)s] %(message)s  (%(pathname)s:%(lineno)s)')

    try:
        msg_type = MsgType[msg_type.upper()]
    except KeyError:
        sys.exit('No such message type: ' + msg_type)
    data = types.Record(types.utils.prettyread(sys.stdin.read()))

    ctrl = DumbController(types.Record(
        CONFIG_ID=cid,
        CONFIG_SERVERS=[types.IPaddr(config.host)],
        CONFIG_SERVER_PORT=config.port,
    ), utils.crypto_box_factory(Database(config.db_url))(cid))

    print('========== With controller config: ==========')
    print(types.utils.prettyprint(ctrl.conf))

    print('============== sending request ==============')
    print('of type {}'.format(msg_type.name))
    print('------------------- data: -------------------')
    print(types.utils.prettyprint(data))

    status, re_data = ctrl.request(msg_type, data)
    print('============= received response =============')
    print('Status: {}'.format(status.name))
    print('------------------- data: -------------------')
    print(types.utils.prettyprint(re_data))
