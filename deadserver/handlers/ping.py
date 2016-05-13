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
    ctx.db.query(
        'UPDATE controller SET last_seen = :t, db_version = :db, fw_version = :fw WHERE id = :ctrl',
        ctrl=controller, t=datetime.now(timezone.utc), db=req.DB_VERSION, fw=req.FW_VERSION)
    return Record(
        TIME=int(datetime.now(timezone.utc).timestamp()),
        DB_VERSION=get_latest_or_0(ctx.cfiles, filetypes.FileType.DB, controller),
        FW_VERSION=get_latest_or_0(ctx.cfiles, filetypes.FileType.FW, controller),
    )
