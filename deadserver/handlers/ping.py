"""Handler for PING requests: keepalive, DB and FW version info"""

from datetime import datetime, timezone
import logging

from common.cfiles import filetypes, fs
from common.types import Record

from .defs import handles, MsgType

log = logging.getLogger(__name__)

def get_latest_or_0(cf, ftype, controller):
    try:
        return filetypes.get_latest(cf, ftype, controller)
    except fs.NoSuchFile as e:
        log.warn('no latest version of {} for #{}'.format(ftype.name, controller))
        return 0


@handles(MsgType.PING)
def handle(controller, req, ctx):
    # Note: Because we promise idempotence, we must avoid setting the same stuff except for
    # last_seen, so that's why the NOT EXISTS
    ctx.db.query(
        '''
        UPDATE controller
        SET last_seen = :t, controller_time = :ct, db_version = :db, fw_version = :fw
        WHERE id = :ctrl AND (NOT EXISTS (
            SELECT * FROM controller
            WHERE id = :ctrl AND controller_time = :ct AND db_version = :db AND fw_version = :fw
        ))
        ''',
        ctrl=controller, t=datetime.now(timezone.utc), db=req.DB_VERSION, fw=req.FW_VERSION,
        ct=datetime.fromtimestamp(req.TIME, timezone.utc))
    return Record(
        TIME=int(datetime.now(timezone.utc).timestamp()),
        DB_VERSION=get_latest_or_0(ctx.cfiles, filetypes.FileType.DB, controller),
        FW_VERSION=get_latest_or_0(ctx.cfiles, filetypes.FileType.FW, controller),
    )
