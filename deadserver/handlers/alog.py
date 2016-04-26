"""Handler for ALOG requests: receive access logs"""

import time

from .defs import handles
from . import utils

from structparse import struct, types
from ..protocol import MsgType, ResponseStatus, show_id

CardId = types.PascalStr(12)

ALOGrequest = struct('ALOGrequest', (types.Uint64, 'time'   ),
                                    (CardId,       'card_id'),
                                    (types.Uint8,  'allowed'))

@handles(MsgType.ALOG)
@utils.unpack_indata_as(ALOGrequest)
def handle(controller_id, data, api):
    # TODO error handling :D
    api.db.query('INSERT INTO accesslog (time, controller_id, card, allowed) '
                 '    VALUES (:t, (SELECT id FROM controller WHERE mac = :ctrl), :card, :a)',
                 t=time.ctime(data.time.val), ctrl=show_id(controller_id), card=data.card_id.val,
                 a=bool(data.allowed.val))
    return ResponseStatus.OK, None
