"""This knows the wire format for the various structures in the protocol."""

import os

import cbor

from common.types import Record
from common.types.serializable import cbor_encode, cbor_decode
from .constants import MsgType, ResponseStatus

from . import crypto, utils

### MESSAGES #######################################################################################

def write_request(msg_type, indata):
    return cbor.dumps(cbor.Tag(msg_type, cbor_encode(indata)))

def write_response(msg_type, status, outdata):
    return cbor.dumps(cbor.Tag(status, cbor.Tag(msg_type, cbor_encode(outdata))))

def read_request(buf):
    request = cbor.loads(buf)
    utils.check(hasattr(request, 'tag'), 'Request not tagged by type')
    return MsgType(request.tag), cbor_decode(request.value)

def read_response(buf):
    response = cbor.loads(buf)
    utils.check(hasattr(response,       'tag'), 'Response not tagged by status')
    utils.check(hasattr(response.value, 'tag'), 'Response not tagged by type')
    status = ResponseStatus(response.tag)
    msg_type = MsgType(response.value.tag)
    data = cbor_decode(response.value.value)
    return msg_type, status, data

### OUTER ENVELOPE #################################################################################

MAGIC = b'DEAD'  # magic number identifying Deadlock messages
PROTOCOL_VERSION = 1

def new_envelope(controller):
    return Record(
        VERSION=PROTOCOL_VERSION,
        CONTROLLER=controller,
        NONCE=os.urandom(crypto.NONCE_SIZE),
    )

def re_nonce(nonce):
    r = bytearray(nonce)
    r[-1] ^= 0x1
    return bytes(r)

def re_envelope(envelope):
    """Fills in fields of a response envelope according to the original one. PAYLOAD is unset."""
    return Record(
        VERSION=envelope.VERSION,
        CONTROLLER=envelope.CONTROLLER,
        NONCE=re_nonce(envelope.NONCE),
    )

def open_envelope(buf, get_crypto_box):
    """Parses the outer envelope from the wire format, checking what needs checking.

    Returns parsed envelope and decrypted payload.
    get_crypto_box: controller ID -> CryptoBox
    """
    utils.check(buf[:len(MAGIC)] == MAGIC, 'Not a Deadlock message')
    envelope = cbor_decode(cbor.loads(buf[len(MAGIC):]))
    utils.check(envelope.VERSION == PROTOCOL_VERSION, 'Unknown protocol version')
    crypto_box = get_crypto_box(envelope.CONTROLLER)
    return envelope, crypto_box.decrypt(envelope.NONCE, envelope.PAYLOAD)

def close_envelope(envelope, payload, get_crypto_box):
    """Closes the envelope with the given payload inside -- returns the wire format."""
    crypto_box = get_crypto_box(envelope.CONTROLLER)
    envelope.PAYLOAD = crypto_box.encrypt(nonce=envelope.NONCE, payload=payload)
    return MAGIC + cbor.dumps(cbor_encode(envelope))
