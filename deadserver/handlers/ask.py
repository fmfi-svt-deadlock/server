"""Handler for ASK requests: should I allow access now?"""

from datetime import datetime, timezone

from common import rules
from structparse import struct, types

from common.utils.cbor import deadlock_tags as T

from ..protocol import MsgType, ResponseStatus, show_id
from .defs import handles
from . import utils

@handles(MsgType.ASK)
@utils.deserialize_in
@utils.serialize_out
def handle(controller, data, api):
    accesspoint_r = api.db.query(
        'SELECT p.id FROM accesspoint p JOIN controller c ON p.controller = c.id'
        ' WHERE c.mac = :ctrl', ctrl=show_id(controller)).all()
    if not accesspoint_r:
        raise ValueError('no associated accesspoint for controller {}'.format(show_id(controller)))
    accesspoint = accesspoint_r[0][0]
    identity_r = api.db.query('SELECT id FROM identity WHERE card = :c', c=data[T.CARD_ID]).all()
    if not identity_r: return NO
    identity = identity_r[0][0]
    print(accesspoint, identity)
    return {
        T.STATUS: ResponseStatus.OK,
        T.ALLOW: rules.ask(api.db, accesspoint, datetime.now(timezone.utc), identity),
    }
