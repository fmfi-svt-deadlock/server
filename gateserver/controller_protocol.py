"""Implements the Controller <-> Server protocol.

See https://github.com/fmfi-svt-gate/server/wiki/Controller-%E2%86%94-Server-Protocol .
"""

from .utils.structparse import *
import nacl.raw as nacl
from enum import Enum

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

Packet = mystruct('Packet',
                  (t.bytes(2) , 'protocol_version'),
                  (t.bytes(6) , 'controller_id'   ),
                  (t.bytes(18), 'nonce'           ),
                  (t.tail     , 'payload'         ))

Request = mystruct('Request',
                   (t.uint8, 'msg_type'),
                   (t.tail , 'data'    ))

Response = mystruct('Response',
                    (t.uint8, 'msg_type'),
                    (t.uint8, 'status'  ),
                    (t.tail , 'data'    ))

def crypto_unwrap_payload(packet, key):
    return nacl.crypto_secretbox_open(packet.payload,
        packet.controller_id + packet.nonce, key)

def crypto_wrap_payload(payload, controller_id, nonce, key):
    return nacl.crypto_secretbox(payload,
        controller_id + nonce, key)

def parse_packet(buf):
    """Parses the packet header, returning that and the rest of the data."""
    try:
        p = Packet.unpack(buf)
    except ValueError as e:
        raise BadMessageError(e.args)
    checkmsg(p.protocol_version == PROTOCOL_VERSION, 'Invalid protocol version')
    return p

def parse_payload(struct, packet, key):
    """Decrypts the payload and parses the request/response header.

    struct: Request or Response
    Returns the parsed payload (as struct).
    """
    assert struct in [Request, Response]
    try:
        payload = crypto_unwrap_payload(packet, key)
    except ValueError as e:
        raise BadMessageError('Decryption failed') from e
    r = struct.unpack(payload)
    try:
        _ = MsgType(r.msg_type) # check it is valid; TODO change to MsgType during unpack()
    except ValueError as e:
        raise BadMessageError('Unknown message type') from e
    return r

def parse_request(packet, key):
    return parse_payload(Request, packet, key)

def parse_response(packet, key):
    return parse_payload(Response, packet, key)

def make_packet(controller_id, key, nonce, r):
    """Packs and encrypts the packet headers, request/response headers and data.
    """
    encrypted = crypto_wrap_payload(r.pack(), controller_id, nonce, key)
    return Packet(protocol_version=PROTOCOL_VERSION,
                  controller_id=controller_id,
                  nonce=nonce,
                  payload=encrypted)

def make_response_packet_for(in_packet, key, request, status, data=None):
    """Creates a response packet from the status and data for the given request.

    Packs status and data into a response, encrypting according to `packet_head`
    and `key`. Requires `packet_head` and `request_head` to be valid.
    """
    if not data: data = b''
    response = Response(msg_type=request.msg_type,
                        status=status.value,
                        data=data)
    response_nonce = bytearray(in_packet.nonce); response_nonce[-1] ^= 0x1
    return make_packet(in_packet.controller_id, key, response_nonce, response)
