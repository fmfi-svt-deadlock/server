"""Handler for XFER requests: transfer a file chunk"""

from .defs import handles
from . import utils

from common import cfiles
from common import filetypes

from structparse import struct, types
from ..protocol import MsgType, ResponseStatus

Request = struct('Request',
                 (filetypes.FileType, 'type'   ),
                 (types.Uint32,       'version'),
                 (types.Uint32,       'offset' ),
                 (types.Uint32,       'length' ))

Response = struct('Response',
                  (types.Uint32, 'length'),
                  (types.Tail,   'chunk' ))

@handles(MsgType.XFER)
@utils.deserialize_in
@utils.serialize_out
def handle(controller_id, req, api):
    filename = filetypes.filename(type=req.type, version=req.version.val)
    try:
        with api.cfiles.find_for(controller_id, filename) as f:
            f.seek(req.offset.val)
            chunk = f.read(req.length.val)
            return ResponseStatus.OK, Response(len(chunk), chunk)
    except ValueError as e:  # file not found
        return ResponseStatus.TRY_AGAIN, None
