"""Handler for ALOG requests: receive access logs"""

import time

from sqlalchemy.exc import IntegrityError

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
    """Handles the ALOG message.

    Messages are idempotent, which in this case means that every particular (controller, time,
    card_id, allowed) combination will be recorded at most once, even if such a packet is received
    multiple times.
    """
    # TODO this query could use ON CONFLICT DO NOTHING, but that only exists with Postgres>=9.5 Am I
    # allowed to require that?
    # For now just doing nothing by silencing that particular IntegrityError. This requires this
    # code to know the name of that particular UNIQUE constraint, which is ugly, but it works with
    # old Postgres.
    try:
        api.db.query(
            '''
            INSERT INTO accesslog (time, controller, card, allowed)
            VALUES (:t, (SELECT id FROM controller WHERE mac = :ctrl), :card, :a)
            ''',
            t=time.ctime(data.time.val), ctrl=show_id(controller_id), card=data.card_id.val,
            a=bool(data.allowed.val))
    except IntegrityError as e:
        if not ('record_unique' in repr(e) and 'duplicate' in repr(e)):
            raise e
    return ResponseStatus.OK, None  # all errors raise, so if I get here, it is in the DB
