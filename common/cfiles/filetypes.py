import enum
import re
import os

import parse

from common import tags as T

from . import fs

FILENAME_PATTERN = '{ftype}_{version:010d}.bin'
LATEST_PATTERN   = '{ftype}_latest.bin'

class FileType(enum.Enum):
    DB = T.FILETYPE_DB
    FW = T.FILETYPE_FW

def filename(ftype, version):
    return FILENAME_PATTERN.format(ftype=ftype.name, version=version)

def latest_filename(ftype):
    return LATEST_PATTERN.format(ftype=ftype.name)

def set_latest(fs, ftype, version, controller=None):
    real = fs.path(filename(ftype, version), controller)
    link = fs.path(latest_filename(ftype), controller)
    os.symlink(real, link)

def get_latest(fs, ftype, controller=None):
    fullname = os.readlink(fs.path_with_common(latest_filename(ftype), controller))
    return filemeta(os.path.basename(fullname))[1]

def filemeta(filename):
    metadata = parse.parse(FILENAME_PATTERN, filename)
    return FileType[metadata['ftype']], metadata['version']
