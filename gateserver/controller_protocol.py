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

Packet = mystruct('Packet',
                  (t.bytes(2) , 'protocol_version'),
                  (t.bytes(6) , 'controller_id'   ),
                  (t.bytes(18), 'nonce'           ))

Request = mystruct('Request',
                   (t.uint8, 'msg_type'))

Response = mystruct('Response',
                    (t.uint8, 'msg_type'),
                    (t.uint8, 'status'  ))

def crypto_unwrap(packet, key, payload):
    return nacl.crypto_secretbox_open(payload,
        packet.controller_id + packet.nonce, key)

def crypto_wrap(packet, key, payload):
    return nacl.crypto_secretbox(payload,
        packet.controller_id + packet.nonce, key)

def parse_packet(buf):
    """Parses the packet into a `Packet` struct with the body in `tail`."""
    packet = Packet.unpack_with_tail(buf)
    checkmsg(packet.protocol_version == PROTOCOL_VERSION,
        'Invalid protocol version')
    return packet

def payload_from_packet(payload_struct, packet, key):
    """Decrypts the packet payload and parses the request/response header.

    Returns the parsed payload (as struct), with the `msg_type_e` property set
    to the parsed `MsgType`.
    """
    assert payload_struct in [Request, Response]
    try:
        payload = crypto_unwrap(packet, key, packet.tail)
    except ValueError as e:
        raise BadMessageError('Decryption failed') from e
    parsed = payload_struct.unpack_with_tail(payload)
    try:
        parsed.msg_type_e = MsgType(parsed.msg_type)
    except ValueError as e:
        raise BadMessageError('Unknown message type') from e
    return parsed

def request_from_packet(packet, key):
    """Decrypts the request packet payload and parses the request.

    Returns the parsed Request, with the `msg_type_e` property set
    to the parsed `MsgType`.
    """
    return payload_from_packet(Request, packet, key)

def response_from_packet(packet, key):
    """Decrypts the response packet payload and parses the response.

    Returns the parsed Response, with the `msg_type_e` and `status_e` properties
    set to the parsed `MsgType` and `ResponseStatus`, respectively.
    """
    response = payload_from_packet(Response, packet, key)
    try:
        response.status_e = ResponseStatus(response.status)
    except ValueError:
        raise BadMessageError('Unknown status {}'.format(response.status))
    return response

def response_packet_for(request_packet, response, key):
    """Creates a response Packet for the given request Packet and Response.

    Packs Response, encrypting according to `request_packet` and `key`. Requires
    `request_packet` and `response` to be valid.
    """
    response_nonce = bytearray(request_packet.nonce); response_nonce[-1] ^= 0x1
    response_packet = Packet(PROTOCOL_VERSION,
                             request_packet.controller_id,
                             response_nonce)
    response_payload = crypto_wrap(response_packet, key, response.pack())
    response_packet.tail = response_payload
    return response_packet
