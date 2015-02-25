"""Implements the Controller <-> Server protocol.

See https://github.com/fmfi-svt-gate/server/wiki/Controller-%E2%86%94-Server-Protocol .
"""

from .utils.structparse import *
import nacl.raw as nacl

PROTOCOL_VERSION = bytes([0x00,0x01])

class BadMessageError(Exception): pass

def checkmsg(expression, errmsg):
    if not expression: raise BadMessageError(errmsg)

class MsgType(Enum):
    OPEN = 1

class ResponseStatus(Enum):
    OK        = 0x01
    ERR       = 0x10
    TRY_AGAIN = 0x11

PacketHead = mystruct('PacketHead',
                      (t.bytes(2) , 'protocol_version'),
                      (t.bytes(6) , 'controllerID'    ),
                      (t.bytes(18), 'nonce'           ))

RequestHead = mystruct('RequestHead',
                       (t.uint8, 'msg_type'))

ResponseHead = mystruct('ResponseHead',
                     (t.uint8, 'msg_type'),
                     (t.uint8, 'status'  ))

def crypto_unwrap(packet_head, key, payload):
    return nacl.crypto_secretbox_open(payload,
        packet_head.controllerID + packet_head.nonce, key)

def crypto_wrap(packet_head, key, payload):
    return nacl.crypto_secretbox(payload,
        packet_head.controllerID + packet_head.nonce, key)

def parse_packet_head(buf):
    """Parses the packet header, returning that and the rest of the data."""
    p, payload = PacketHead.unpack_from(buf)
    checkmsg(p.protocol_version == PROTOCOL_VERSION, 'Invalid protocol version')
    return p, payload

def parse_payload(struct, packet_head, key, payload):
    """Decrypts the payload and parses the request/response header.

    Returns the parsed header (as struct), message type (as MsgType) and the
    rest of the data.
    """
    assert struct in [RequestHead, ResponseHead]
    try:
        payload = crypto_unwrap(packet_head, key, payload)
    except ValueError as e:
        raise BadMessageError('Decryption failed') from e
    r, data = struct.unpack_from(payload)
    try:
        t = MsgType(r.msg_type)
    except ValueError as e:
        raise BadMessageError('Unknown message type') from e
    return r, t, data

def parse_request(packet_head, key, payload):
    return parse_payload(RequestHead, packet_head, key, payload)

def parse_response(packet_head, key, payload):
    return parse_payload(ResponseHead, packet_head, key, payload)

def make_packet(packet_head, r_head, key, data=None):
    """Packs and encrypts the packet headers, request/response headers and data.

    Requires `packet_head` and `r_head` to be valid."""
    payload = r_head.pack() + (data or b'')
    return packet_head.pack() + crypto_wrap(packet_head, key, payload)

def make_response_for(packet_head, request_head, key, status, data=None):
    """Creates a response for the given packet and request headers.

    Packs status and data into a response, encrypting according to `packet_head`
    and `key`. Requires `packet_head` and `request_head` to be valid.
    """
    response_nonce = bytearray(packet_head.nonce); response_nonce[-1] ^= 0x1
    response_packet_head = PacketHead(protocol_version=PROTOCOL_VERSION,
                                   controllerID=packet_head.controllerID,
                                   nonce=response_nonce)
    response_head = ResponseHead(msg_type=request_head.msg_type, status=status.value)
    return make_packet(response_packet_head, response_head, key, data)
