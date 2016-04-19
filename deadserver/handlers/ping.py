"""Handler for PING requests: keepalive, DB and FW version info"""

import time
from datetime import datetime

from structparse import struct, types
from common import filetypes

from .. import protocol
from ..protocol import MsgType, ResponseStatus
from .defs import handles
from . import utils

Ping = struct('Ping',
              (types.Uint64, 'time'      ),
              (types.Uint32, 'db_version'),
              (types.Uint32, 'fw_version'))

@handles(MsgType.PING)
@utils.unpack_indata_as(Ping)
@utils.pack_outdata
def handle(controller_id, req, api):
    api.db.query("UPDATE controller SET last_seen = :t, db_version = :db, fw_version = :fw WHERE mac = :id",
                 id=protocol.id2str(controller_id), t=datetime.now(),
                 db=req.db_version.val, fw=req.fw_version.val)

    available_files = [ filetypes.filemeta(f) for f in api.cfiles.ls_for(controller_id) ]
    db_versions = [ v for t, v in available_files if t == filetypes.FileType.DB ]
    fw_versions = [ v for t, v in available_files if t == filetypes.FileType.FW ]

    return ResponseStatus.OK, Ping(time=int(time.time()),
                                   db_version=max(db_versions, default=0),
                                   fw_version=max(fw_versions, default=0))

