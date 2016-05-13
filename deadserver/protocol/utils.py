import base64
import binascii
import logging

from .constants import MsgType, ResponseStatus
from . import crypto, errors

def check(expression, errmsg):
    if not expression: raise errors.BadMessageError(errmsg)


def show_nonce(nonce):
    """Returns string representation of the nonce. Shortens to first 4 bytes only."""
    return binascii.hexlify(nonce[:4]).decode('ascii')


class MessageLogger:
    def __init__(self, loggername):
        self.log = logging.getLogger(loggername)

    def request(self, envelope, msg_type):
        self.log.info('<-{ctrl} [{nonce}] {type}'.format(
            ctrl=envelope.CONTROLLER,
            type=msg_type.name,
            nonce=show_nonce(envelope.NONCE)))

    def response(self, envelope, msg_type, status):
        self.log.info('->{ctrl} [{nonce}] {type} {status}'.format(
            ctrl=envelope.CONTROLLER,
            type=msg_type.name,
            nonce=show_nonce(envelope.NONCE),
            status=status.name))

    def status_error(self, controller, msg_type, e):
        self.log.warn('{type} ->{ctrl} {kind} ERROR: {msg}'.format(
            ctrl=controller, type=msg_type.name, msg=e.message, kind=('SOFT' if e.soft else'HARD')))

    def bad_message(self, buf, e, maxlen):
        self.log.exception('BAD MSG: {arg} -- buf: [size {size}] {buf}'.format(
            arg=' '.join(e.args), size=len(buf),
            buf=base64.b64encode(buf[:maxlen]).decode('ascii')))

    def __getattr__(self, attr):
        # proxy everything else to self.log
        return getattr(self.log, attr)


# A Box Factory Factory! Today is a good day! Err...
def crypto_box_factory(db):
    def get_box(controller):
        r = db.query('SELECT key FROM controller WHERE id = :id', id=controller).all()
        if not r: raise ValueError('unknown controller ID')
        key = bytes(r[0]['key'])
        return crypto.CryptoBox(key)
    return get_box
