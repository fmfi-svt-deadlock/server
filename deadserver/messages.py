"""The controller ↔ server protocol message handler.

Reads messages and passes them to the appropriate handlers defined in `handlers/*.py`.
"""

from constants.enums import MsgType, ResponseStatus
from common import cfiles

from . import handlers
from .protocol import errors, utils, wirefmt

class Context:
    def __init__(self, config, db):
        self.config         = config
        self.db             = db
        self.cfiles         = cfiles.ControllerFiles(self.config.controller_files_path)

class MessageHandler:
    def __init__(self, ctx):
        self.ctx = ctx
        self.log = utils.MessageLogger(__name__)
        self.allowed_msg_types = {MsgType[x] for x in self.ctx.config.allowed_msg_types}
        self.get_crypto_box = utils.crypto_box_factory(self.ctx.db)

    def handle(self, in_buf):
        try:
            envelope, payload = wirefmt.open_envelope(in_buf, self.get_crypto_box)
            msg_type, indata = wirefmt.read_request(payload)
            self.log.request(envelope, msg_type)
            status, outdata = self.pass_to_handlers(envelope.CONTROLLER, msg_type, indata)
            out = wirefmt.write_response(msg_type, status, outdata)
            self.log.response(envelope, msg_type, status)
            return wirefmt.close_envelope(wirefmt.re_envelope(envelope), out, self.get_crypto_box)
        except (ValueError, errors.BadMessageError) as e:
            self.log.bad_message(in_buf, e, getattr(self.ctx.config, 'log_message_bytes', 1024))
            # don't send an error response -- we don't want to be a padding oracle or something

    def pass_to_handlers(self, controller, msg_type, indata):
        utils.check(msg_type in self.allowed_msg_types,
                    'Not a supported message type: {}'.format(msg_type))
        handler = handlers.get_handler_for(msg_type)
        status = None
        try:
            outdata = handler(controller, indata, ctx=self.ctx)
            status = ResponseStatus.OK
        except errors.StatusError as e:
            status = ResponseStatus.TRY_AGAIN if e.soft else ResponseStatus.ERR
        return status, outdata
