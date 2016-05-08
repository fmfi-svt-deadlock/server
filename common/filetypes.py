"""TODO"""

import enum
import re

from common import deadlock_tags as T

class FileType(enum.Enum):
    DB = T.FILETYPE_DB
    FW = T.FILETYPE_FW

def filename(ftype, version):
    return '{}_{:010d}.bin'.format(ftype.name, version)

def filemeta(filename):
    t, v = re.match(r'([^_]+)_(\d+).bin', filename).group(1,2)
    return FileType[t], int(v)
