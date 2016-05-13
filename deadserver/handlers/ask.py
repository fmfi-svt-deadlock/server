"""Handler for ASK requests: should I allow access now?"""

from datetime import datetime, timezone

from common import rules
from common.types import Record

from .defs import handles, MsgType

@handles(MsgType.ASK)
def handle(controller, data, ctx):
    # TODO transaction
    accesspoint_r = ctx.db.query('SELECT id FROM accesspoint WHERE controller = :ctrl',
                                 ctrl=controller).all()
    if not accesspoint_r:
        raise ValueError('no associated accesspoint for controller {}'.format(controller))
    accesspoint = accesspoint_r[0][0]
    identity_r = ctx.db.query('SELECT id FROM identity WHERE card = :c', c=data.CARD_ID).all()
    if not identity_r: return Record(ALLOWED=False)
    identity = identity_r[0][0]
    return Record(ALLOWED=rules.ask(ctx.db, accesspoint, datetime.now(timezone.utc), identity))
