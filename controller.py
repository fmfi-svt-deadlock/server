"""Quick & dirty client (i.e. the controller end), used for manual testing of the server."""

import ipaddress
import random
import socket
import sys

from records import Database

import config
from common import mycbor
from constants.enums import MsgType
from deadserver.protocol import utils, wirefmt

MAGIC = b'DEAD'
PROTOCOL_VERSION = 1

# TODO it's assymetric
class DumbController:
    """An implementation of the controller. Kinda dumb, for debugging purposes only."""
    def __init__(self, conf, crypto_box):
        self.conf = conf
        self.conf.CONFIG_KEY = '(not needed -- using CryptoBox)'
        self.id = conf.CONFIG_ID
        self.crypto_box = lambda _: crypto_box  # lambda because wirefmt accepts functions

    def request(self, msg_type, data):
        """This does not check anything in the response, as it is dumb (on purpose)."""
        req_buf = wirefmt.write_request(msg_type, data)



        import binascii
        print('req_buf:', binascii.hexlify(req_buf))



        out_buf = wirefmt.close_envelope(wirefmt.new_envelope(self.id), req_buf, self.crypto_box)
        in_buf = self._send(out_buf)
        re_envelope, response_buf = wirefmt.open_envelope(in_buf, self.crypto_box)
        re_msg_type, status, re_data = wirefmt.read_response(response_buf)
        utils.check(re_msg_type == msg_type,
                    'Got OT response: {} (expected {})'.format(re_msg_type.name, msg_type.name))
        return status, re_data

    def _send(self, buf):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = random.choice(self.conf.CONFIG_SERVERS)
        sock.sendto(buf, (host.exploded, self.conf.CONFIG_SERVER_PORT))
        return sock.recv(64000)

if __name__ == '__main__':
    cid, msg_type = int(sys.argv[1]), sys.argv[2]
    try:
        msg_type = MsgType[msg_type.upper()]
    except KeyError:
        sys.exit('No such message type: ' + msg_type)
    data = mycbor.RecordDL(mycbor.pretty.read(sys.stdin.read()))

    ctrl = DumbController(mycbor.RecordDL(
        CONFIG_ID=cid,
        CONFIG_SERVERS=[mycbor.IPaddr(config.host)],
        CONFIG_SERVER_PORT=config.port,
    ), utils.crypto_box_factory(Database(config.db_url))(cid))

    print('========== With controller config: ==========')
    print(mycbor.pretty.show(ctrl.conf))

    print('============== sending request ==============')
    print('of type {}'.format(msg_type.name))
    print('------------------- data: -------------------')
    print(mycbor.pretty.show(data))

    status, re_data = ctrl.request(msg_type, data)
    print('============= received response =============')
    print('Status: {}'.format(status.name))
    print('------------------- data: -------------------')
    print(mycbor.pretty.show(re_data))

