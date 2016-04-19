"""TODO"""

import enum
import re

import structparse

class FileType(structparse.types.Uint8, enum.Enum):
    DB = 1
    FW = 2

def filename(ftype, version):
    return '{}_{:010d}.bin'.format(ftype.name, version)

def filemeta(filename):
    t, v = re.match(r'([^_]+)_(\d+).bin', filename).group(1,2)
    return FileType[t], int(v)
