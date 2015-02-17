"""Implements the Controller <-> Server protocol.

See https://github.com/fmfi-svt-gate/server/wiki/Controller-%E2%86%94-Server-Protocol .
"""

from .utils.structparse import *
import nacl.raw as nacl

PROTOCOL_VERSION = bytes([0x00,0x01])

class BadMessageError(Exception):
    def __init__(self, message, data=None):
        self.message = message
        self.data    = data
        super().__init__(message)

def checkmsg(expression, errmsg, data=None):
    if not expression: raise BadMessageError(errmsg, data)

class MsgType(Enum):
    OPEN = 1

class ReplyStatus(Enum):
    OK        = 0x01
    ERR       = 0x10
    TRY_AGAIN = 0x11
S = ReplyStatus

PacketHead = mystruct('PacketHead',
                     ['protocol_version', 'controllerID', 'nonce'      ],
                     [ t.bytes(2)       ,  t.bytes(6)   ,  t.bytes(18) ])

RequestHead = mystruct('RequestHead',
                      ['msg_type'],
                      [ t.uint8  ])

ReplyHead = mystruct('ReplyHead',
                    ['msg_type', 'status' ],
                    [ t.uint8  ,  t.uint8 ])

def crypto_unwrap(packet_head, key, payload):
    return nacl.crypto_secretbox_open(payload,
        packet_head.controllerID + packet_head.nonce, key)

def crypto_wrap(packet_head, key, payload):
    return nacl.crypto_secretbox(payload,
        packet_head.controllerID + packet_head.nonce, key)

def parse_packet_head(buf):
    """Parses the packet header, returning that and the rest of the data."""
    p, payload = PacketHead.unpack_from(buf)
    checkmsg(p.protocol_version == PROTOCOL_VERSION,
             'Invalid protocol version', p.protocol_version)
    return p, payload

def parse_r(struct, packet_head, key, payload):
    """Decrypts the payload and parses the request/reply header.

    Returns the parsed header (as struct), message type (as MsgType) and the
    rest of the data.
    """
    assert struct in [RequestHead, ReplyHead]
    try: payload = crypto_unwrap(packet_head, key, payload)
    except ValueError as e: raise BadMessageError('Decryption failed') from e
    r, data = struct.unpack_from(payload)
    try: t = MsgType(r.msg_type)
    except ValueError as e: raise BadMessageError('Unknown message type') from e
    return r, t, data

def make_packet(packet_head, r_head, key, data=None):
    """Packs and encrypts the packet headers, request/reply headers and data.

    Requires `packet_head` and `r_head` to be valid."""
    payload = r_head.pack() + (data or bytes(0))
    return packet_head.pack() + crypto_wrap(packet_head, key, payload)

def make_reply_for(packet_head, request_head, key, status, data=None):
    """Creates a reply for the given packet and request headers.

    Packs status and data into a reply, encrypting according to `packet_head`
    and `key`. Requires `packet_head` and `request_head` to be valid.
    """
    nnonce = bytearray(packet_head.nonce); nnonce[-1] ^= 0x1
    p = PacketHead(protocol_version=PROTOCOL_VERSION,
                   controllerID=packet_head.controllerID,
                   nonce=nnonce)
    r = ReplyHead(msg_type=request_head.msg_type, status=status.value)
    return make_packet(p, r, key, data)
