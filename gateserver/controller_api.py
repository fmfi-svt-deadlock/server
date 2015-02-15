from .utils.structparse import *
from . import utils
from . import db
import nacl.raw as nacl

PROTOCOL_VERSION = bytes([0x00,0x01])

class BadMessageError(Exception): pass

def checkmsg(expression, err):
    if not expression: raise BadMessageError(err)

class MsgType(Enum):
    OPEN = 1

class ReplyStatus(Enum):
    OK = 0x01
    ERR = 0x10
    TRY_AGAIN = 0x11
S = ReplyStatus

PacketHead = mystruct('PacketHead',
                     ['protocol_version', 'controllerID', 'nonce' ],
                     [ t.bytes(2) , t.bytes(6) , t.bytes(18) ])

RequestHead = mystruct('RequestHead',
                      ['msg_type'],
                      [ t.uint8 ])

ReplyHead = mystruct('ReplyHead',
                    ['msg_type', 'status' ],
                    [ t.uint8 , t.uint8 ])

def get_key_for_mac(mac):
    rs = db.exec_sql('SELECT key FROM controller WHERE id = %s',
                     (utils.bytes2mac(mac),), ret=True)
    checkmsg(len(rs) == 1, 'unknown controllerID '+utils.bytes2mac(mac))
    return rs[0]['key'].tobytes()

def crypto_unwrap(packet_head, payload):
    key = get_key_for_mac(packet_head.controllerID)
    return nacl.crypto_secretbox_open(payload,
        packet_head.controllerID + packet_head.nonce, key)

def crypto_wrap(packet_head, payload):
    key = get_key_for_mac(packet_head.controllerID)
    return nacl.crypto_secretbox(payload,
        packet_head.controllerID + packet_head.nonce, key)

def parse_packet(buf, struct=None):
    struct = struct or RequestHead
    assert struct in [RequestHead, ReplyHead]
    p, payload = PacketHead.unpack_from(buf)
    checkmsg(p.protocol_version == PROTOCOL_VERSION, 'Invalid protocol version')
    payload = crypto_unwrap(p, payload)
    r, data = struct.unpack_from(payload)
    try:
        t = MsgType(r.msg_type)
    except ValueError:
        raise BadMessageError('Unknown request type {}'.format(r.msg_type))
    return p, r, t, data

def make_packet(packet_head, r_head, data=None):
    """Requires `packet_head` and `r_head` to be valid."""
    payload = r_head.pack() + (data or bytes(0))
    return packet_head.pack() + crypto_wrap(packet_head, payload)

def make_reply_for(packet_head, request_head, status, data=None):
    """Requires `packet_head` and `request_head` to be valid."""
    nnonce = bytearray(packet_head.nonce); nnonce[-1] ^= 0x1
    p = PacketHead(protocol_version=PROTOCOL_VERSION,
                   controllerID=packet_head.controllerID,
                   nonce=nnonce)
    r = ReplyHead(msg_type=request_head.msg_type, status=status.value)
    return make_packet(p, r, data)

def fstring(buf):
    length, string = int(buf[0]), buf[1:]
    checkmsg(length <= len(string), 'fstring length > buffer size')
    return string[:length]

process_request = {
    MsgType.OPEN:
        lambda data: ((S.OK if fstring(data) == b'Hello' else S.ERR), None),
}
assert set(MsgType) == set(process_request), 'Not all message types are handled'

def handle_request(buf):
    packet_head, request_head, request_type, indata = parse_packet(buf)
    status, outdata = process_request[request_type](indata)
    return make_reply_for(packet_head, request_head, status, outdata)
