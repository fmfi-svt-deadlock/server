"""Handler for OPEN requests: should I open the door now?"""

from .defs import handles
from . import utils

from structparse import struct, types
from ..protocol import MsgType, ResponseStatus

CardId = types.PascalStr(12)

OPENrequest = struct('OPENrequest', (CardId, 'card_id'))

@handles(MsgType.OPEN)
@utils.unpack_indata_as(OPENrequest)
def handle(controller_id, data, api):
    status = ResponseStatus.OK if data.card_id == CardId('hello') else ResponseStatus.ERR
    return status, None
