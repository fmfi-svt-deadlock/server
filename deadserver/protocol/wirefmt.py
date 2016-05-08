"""This knows the wire format for the various structures in the protocol."""

import os

from common import mycbor
from constants.enums import MsgType, ResponseStatus

from . import crypto, utils

### MESSAGES #######################################################################################

def write_request(msg_type, indata):
    return mycbor.dump(mycbor.Tag(msg_type, indata))

def write_response(msg_type, status, outdata):
    return mycbor.dump(mycbor.Tag(status, mycbor.Tag(msg_type, outdata)))

def read_request(buf):
    request = mycbor.load(buf)
    utils.check(hasattr(request, 'tag'), 'Request not tagged by type')
    return MsgType(request.tag), request.value

def read_response(buf):
    response = mycbor.load(buf)
    utils.check(hasattr(response,       'tag'), 'Response not tagged by status')
    utils.check(hasattr(response.value, 'tag'), 'Response not tagged by type')
    return MsgType(response.value.tag), ResponseStatus(response.tag), response.value.value

### OUTER ENVELOPE #################################################################################

MAGIC = b'DEAD'  # magic number identifying Deadlock messages
PROTOCOL_VERSION = 1

def new_envelope(controller):
    return mycbor.RecordDL(
        VERSION=PROTOCOL_VERSION,
        CONTROLLER=controller,
        NONCE=os.urandom(crypto.NONCE_SIZE),
    )

def open_envelope(buf, get_crypto_box):
    """Parses the outer envelope from the wire format, checking what needs checking.

    Returns parsed envelope and decrypted payload.
    get_crypto_box: controller ID -> CryptoBox
    """
    utils.check(buf[:len(MAGIC)] == MAGIC, 'Not a Deadlock message')
    envelope = mycbor.load(buf[len(MAGIC):])
    utils.check(envelope.VERSION == PROTOCOL_VERSION, 'Unknown protocol version')
    crypto_box = get_crypto_box(envelope.CONTROLLER)
    return envelope, crypto_box.decrypt(envelope.NONCE, envelope.PAYLOAD)

def re_envelope(envelope):
    """Fills in fields of a response envelope according to the original one. PAYLOAD is unset."""
    re_nonce = bytearray(envelope.NONCE); re_nonce[-1] ^= 0x1; re_nonce = bytes(re_nonce)
    return mycbor.RecordDL(
        VERSION=envelope.VERSION,
        CONTROLLER=envelope.CONTROLLER,
        NONCE=re_nonce,
    )

def close_envelope(envelope, payload, get_crypto_box):
    """Closes the envelope with the given payload inside -- returns the wire format."""
    crypto_box = get_crypto_box(envelope.CONTROLLER)
    envelope.PAYLOAD = crypto_box.encrypt(nonce=envelope.NONCE, payload=payload)
    return MAGIC + mycbor.dump(envelope)
