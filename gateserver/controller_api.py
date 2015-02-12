from .utils.structparse import *
from . import db
import nacl.raw as nacl

PROTOCOL_VERSION = bytes([0x00,0x01])

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

def parse_request_packet(buf):
    p, payload = PacketHead.unpack_from(buf)
    #cntrl = db.exec_sql('SELECT key FROM controller WHERE id = %s', to_mac(p.controllerID))
    #if len(cntrl) != 1: raise BadMessageError('unknown controllerID ' + p.controllerID)
    #key = cntrl[0].key
    #payload = nacl.crypto_secretbox_open(payload, p.nonce, key)
    checkmsg(p.protocol_version == PROTOCOL_VERSION, 'Invalid protocol version')
    checkmsg(p.nonce[-1] & 0x1 == 0, 'Last bit of request nonce must be 0')
    r, data = RequestHead.unpack_from(payload)
    try:
        t = MsgType(r.msg_type)
    except ValueError:
        raise BadMessageError('Unknown request type {}'.format(r.msg_type))
    return p, r, t, data

def make_reply_packet(packet_head, request_head, status, data):
    """Requires `packet_head` and `request_head` to be valid."""
    nnonce = bytearray(packet_head.nonce); nnonce[-1] |= 0x1
    p = PacketHead(protocol_version=PROTOCOL_VERSION,
                   controllerID=packet_head.controllerID,
                   nonce=nnonce)
    r = ReplyHead(msg_type=request_head.msg_type, status=status.value)
    return p.pack() + r.pack() + (data or bytes(0))

def fstring(buf):
    length, string = int(buf[0]), buf[1:]
    checkmsg(length <= len(string), 'fstring length > buffer size')
    return string[:length]

process_request = {
    MsgType.OPEN:
        lambda data: ((S.OK if fstring(data) == b'Hello' else S.ERR), None),
}

def handle_request(buf):
    packet_head, request_head, request_type, indata = parse_request_packet(buf)
    status, outdata = process_request[request_type](indata)
    return make_reply_packet(packet_head, request_head, status, outdata)
