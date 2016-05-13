"""Handler for XFER requests: transfer a file chunk"""

from .defs import handles, MsgType

from common.cfiles import filetypes, fs
from common.types import Record

from ..protocol import errors

@handles(MsgType.XFER)
def handle(controller, req, ctx):
    ftype = filetypes.FileType(req.FILETYPE)
    filename = filetypes.filename(ftype, req.FILEVERSION)
    try:
        with ctx.cfiles.open_with_common(filename, controller) as f:
            f.seek(req.OFFSET)
            chunk = f.read(req.LENGTH)
            return Record(LENGTH=len(chunk), CHUNK=chunk)
    except fs.NoSuchFile as e:
        raise errors.TransientError('File not found ({} v{})'.format(ftype.name, req.FILEVERSION))
