"""Handler for ASK requests: should I open the door now?"""

from datetime import datetime, timezone

from .defs import handles
from . import utils

from structparse import struct, types
from ..protocol import MsgType, ResponseStatus, show_id

CardId = types.PascalStr(12)

ASKrequest = struct('ASKrequest', (CardId, 'card_id'))

# TODO this belongs somewhere else
def should_open(db, accesspoint, when, identity):
    """Evaluate the rules and return True iff access is allowed.

    Parameters:
    db: something with a `records.Database`-like interface
    accesspoint: ID of the accesspoint, as specified in the DB
    time: `datetime.datetime`
    identity: ID of the identity, as specified in the DB

    You probably want to use this with `common.utils.db.transaction`.
    """
    time    = when.timetz()
    date    = when.date()
    weekday = when.weekday()
    r = db.query('''
        SELECT (rkind = 'ALLOW')
        FROM rule r
             JOIN accesspoint p ON p.type = r.aptype
             JOIN time_spec t ON r.time_spec = t.id
             JOIN in_expr e ON r.expr = e.expr_id
        WHERE p.id = :accesspoint
              AND (t.time_from IS NULL
                   OR ((t.time_from, t.time_to) OVERLAPS (:time, :time + interval '1 second')))
              AND (t.date_from IS NULL
                   OR ((t.date_from, t.date_to) OVERLAPS (:date, :date + interval '1 second')))
              AND (t.weekday_mask IS NULL OR (get_bit(t.weekday_mask, :weekday) = 1))
              AND e.identity_id = :identity
        ORDER BY r.priority DESC
        LIMIT 1
    ''', accesspoint=accesspoint, date=date, time=time, weekday=weekday, identity=identity).all()
    assert len(r) <= 1, 'should_open query returned more than 1 result'
    if not r: return False
    return r[0][0]

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
    return YES if should_open(api.db, accesspoint, datetime.now(timezone.utc), identity) else NO
