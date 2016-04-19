"""The controller ↔ server protocol message structure.

This knows the data format for the various structures in the protocol. See
`api.py` for the behavior / business logic.
"""

# TODO: consider [CBOR](http://cbor.io/).
# TODO: With the faster processor, we probably can afford assymetric crypto. Switch if possible.
# TODO: separate the 2 layers of the protocol
# TODO: ... and then blackboxes instead of secret keys

from structparse import struct, types
import nacl.secret
import enum


class BadMessageError(Exception): pass

def check(expression, errmsg):
    if not expression: raise BadMessageError(errmsg)


PROTOCOL_VERSION = types.Bytes(2)([0,1])

class MsgType(types.Uint8, enum.Enum):
    PING     = 0x01
    XFER     = 0x02
    OPEN     = 0x10
    ECHOTEST = 0xee

class ResponseStatus(types.Uint8, enum.Enum):
    OK        = 0x01
    ERR       = 0x10
    TRY_AGAIN = 0x11

Request = struct('Request',
                 (MsgType,     'msg_type'),
                 (types.Tail,  'data'    ))

Response = struct('Response',
                  (MsgType,        'msg_type'),
                  (ResponseStatus, 'status'  ),
                  (types.Tail,     'data'    ))

PacketHeader = struct('PacketHeader',
                      (types.Bytes(2),  'protocol_version'),
                      (types.Bytes(6),  'controller_id'   ),
                      (types.Bytes(18), 'nonce'           ))

Packet = struct('Packet',
                (PacketHeader, 'header' ),
                (types.Tail,   'payload'))


def id2str(id):
    return ':'.join('{:02x}'.format(x) for x in id.val)

def str2id(s):
    return types.Bytes(6)(bytes.fromhex(s.replace(':', '')))


def crypto_unwrap_payload(nonce, payload, key):
    return nacl.secret.SecretBox(key).decrypt(payload, nonce)

def crypto_wrap_payload(nonce, payload, key):
    # Note: encrypt returns the ciphertext prepended by nonce. We don't want this, so strip it.
    return nacl.secret.SecretBox(key).encrypt(payload, nonce)[nacl.secret.SecretBox.NONCE_SIZE:]

def parse_packet(struct, buf, get_key):
    """Parses the buffer into PacketHeader and `struct`, which must be Request or Response.

    Decrypts the payload with the key returned by the `get_key` function.
    """
    assert struct in [Request, Response]

    try:
        hdr, tail = PacketHeader.unpack_from(buf)
        check(hdr.protocol_version == PROTOCOL_VERSION, 'Invalid protocol version')
        payload_buf = crypto_unwrap_payload(hdr.controller_id.val + hdr.nonce.val,
                                            tail, get_key(hdr.controller_id))
        payload = struct.unpack(payload_buf)
    except ValueError as e:
        raise BadMessageError('parsing packet failed') from e

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
