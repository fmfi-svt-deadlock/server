"""Handler for OPEN requests."""

from .defs import handles
from . import utils

from structparse import struct, types
from deadserver.protocol import MsgType, ResponseStatus

CardId = types.PascalStr(12)

OpenRequest = struct('OpenRequest', (CardId, 'card_id'))

@handles(MsgType.OPEN)
@utils.unpack_indata_as(OpenRequest)
def handle(controller_id, data, api):
    status = ResponseStatus.OK if data.card_id == CardId('hello') else ResponseStatus.ERR
    return status, None
