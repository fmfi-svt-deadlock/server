"""Handler for ALOG requests: receive access logs"""

import time

from sqlalchemy.exc import IntegrityError

from .defs import handles, MsgType

@handles(MsgType.ALOG)
def handle(controller, data, ctx):
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
        ctx.db.query(
            'INSERT INTO accesslog (time, controller, card, allowed) VALUES (:t, :ctrl, :card, :a)',
            t=time.ctime(data.TIME), ctrl=controller, card=data.CARD_ID, a=data.ALLOWED)
    except IntegrityError as e:
        if not ('record_unique' in repr(e) and 'duplicate' in repr(e)):
            raise e
