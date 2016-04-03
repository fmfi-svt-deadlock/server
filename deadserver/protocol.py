"""The controller ↔ server protocol message structure.

This knows the data format for the various structures in the protocol. See
`controller_api` for the behavior / business logic.
"""

# TODO: consider [CBOR](http://cbor.io/).
# TODO: With the faster processor, we probably can afford assymetric crypto. Switch if possible.

from structparse import mystruct, types
import nacl.raw as nacl
from enum import Enum

class BadMessageError(Exception): pass

def check(expression, errmsg):
    if not expression: raise BadMessageError(errmsg)

PROTOCOL_VERSION = types.Bytes(2)([0,1])

class MsgType(types.Uint8, Enum):
    OPEN = 1

class ResponseStatus(types.Uint8, Enum):
    OK        = 0x01
    ERR       = 0x10
    TRY_AGAIN = 0x11

Request = mystruct('Request',
                   (MsgType,     'msg_type'),
                   (types.Tail,  'data'    ))

Response = mystruct('Response',
                    (MsgType,        'msg_type'),
                    (ResponseStatus, 'status'  ),
                    (types.Tail,     'data'    ))

PacketHeader = mystruct('PacketHeader',
                        (types.Bytes(2),  'protocol_version'),
                        (types.Bytes(6),  'controller_id'   ),
                        (types.Bytes(18), 'nonce'           ))

Packet = mystruct('Packet',
                  (PacketHeader, 'header'),
                  (types.Tail,   'payload'))

def id2str(id):
    return ':'.join('{:02x}'.format(x) for x in id.val)

def str2id(s):
    return types.Bytes(6)(bytes.fromhex(s.replace(':', '')))

def crypto_unwrap_payload(nonce, payload, key):
    return nacl.crypto_secretbox_open(payload, nonce, key)

def crypto_wrap_payload(nonce, payload, key):
    return nacl.crypto_secretbox(payload, nonce, key)

def parse_packet(struct, buf, get_key):
    """Parses the buffer into PacketHeader and `struct`, which must be Request or Response.

    Decrypts the payload with the key returned by the `get_key` function.
    """
    assert struct in [Request, Response]

    try:
        hdr, tail = PacketHeader.unpack(buf)
        check(hdr.protocol_version == PROTOCOL_VERSION, 'Invalid protocol version')
        payload_buf = crypto_unwrap_payload(hdr.controller_id.val + hdr.nonce.val,
                                            tail, get_key(hdr.controller_id))
        payload = struct.unpack_all(payload_buf)
    except ValueError as e:
        raise BadMessageError('parse_packet failed') from e

    return hdr, payload

def make_packet(controller_id, nonce, payload, get_key):
    """Packs and encrypts the packet headers, request/response headers and data."""
    encrypted = crypto_wrap_payload(controller_id.val + nonce, payload.pack(), get_key(controller_id))
    return Packet(PacketHeader(protocol_version=PROTOCOL_VERSION,
                               controller_id=controller_id,
                               nonce=nonce),
                  encrypted)

def make_response_packet_for(request_header, msg_type, status, response_data, get_key):
    """Creates a response packet from the status and data for the given request.

    Packs status and data into a response, encrypting according to the key returned by `get_key`.
    Requires `request_packet` to be valid.
    """
    if not response_data: response_data = b''
    response = Response(msg_type=msg_type,
                        status=status,
                        data=response_data)
    response_nonce = bytearray(request_header.nonce.val); response_nonce[-1] ^= 0x1
    return make_packet(request_header.controller_id, response_nonce, response, get_key)
