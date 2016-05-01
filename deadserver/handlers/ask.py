"""Handler for ASK requests: should I open the door now?"""

from datetime import datetime, timezone

from common import rules
from structparse import struct, types

from ..protocol import MsgType, ResponseStatus, show_id
from .defs import handles
from . import utils

CardId = types.PascalStr(12)

ASKrequest = struct('ASKrequest', (CardId, 'card_id'))

YES = (ResponseStatus.OK, None)
NO = (ResponseStatus.ERR, None)

@handles(MsgType.ASK)
@utils.unpack_indata_as(ASKrequest)
def handle(controller, data, api):
    accesspoint_r = api.db.query(
        'SELECT p.id FROM accesspoint p JOIN controller c ON p.controller_id = c.id'
        ' WHERE c.mac = :ctrl', ctrl=show_id(controller)).all()
    if not accesspoint_r:
        raise ValueError('no associated accesspoint for controller {}'.format(show_id(controller)))
    accesspoint = accesspoint_r[0][0]
    identity_r = api.db.query('SELECT id FROM identity WHERE card = :c', c=data.card_id.val).all()
    if not identity_r: return NO
    identity = identity_r[0][0]
    print(accesspoint, identity)
    return YES if rules.ask(api.db, accesspoint, datetime.now(timezone.utc), identity) else NO
