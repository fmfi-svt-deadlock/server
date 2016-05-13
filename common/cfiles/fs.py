"""Controller files: opens files meant to be transferred to controllers via the XFER message."""

import errno
import logging
import os

COMMON_DIR = 'common'

log = logging.getLogger(__name__)

class NoSuchFile(RuntimeError):
    def __init__(self, name, controller):
        self.name = name
        self.controller = controller

def mkdirnx(path):
    """mkdir if does not exist"""
    try:
        os.mkdir(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class ControllerFiles():
    def __init__(self, directory):
        self.directory = directory

    def path(self, name, controller=None):
        """Returns the real path to the file for this controller.

        `controller` can be either a controller ID, or `None` for files common to all controllers.
        """
        if os.sep in name: raise ValueError('file name may not contain directories')
        for_dir = '{:010d}'.format(controller) if controller else COMMON_DIR
        real_name = os.path.join(self.directory, for_dir, name)
        log.debug('resolved {} for #{} -> {}'.format(name, controller or 'COMMON', real_name))
        return real_name

    def open(self, name, controller=None, *args, **kwargs):
        """Opens files for the given controller.

        `controller` can be either a controller ID, or `None` for files common to all controllers.

        See also `open_for` and `path_for`.
        """
        real_name = self.path(name, controller)
        mkdirnx(os.path.dirname(real_name))
        return open(real_name, *args, **kwargs)

    def path_with_common(self, name, controller=None):
        """Resolves a path: if this file for this controller doesn't exist, returns a common one.

        Returns the real path to the file.
        """
        real_name = self.path(name, controller)
        if not os.path.exists(real_name): real_name = self.path(name, None)
        if not os.path.exists(real_name): raise NoSuchFile(name, controller)
        return real_name

    def open_with_common(self, name, controller=None):
        """Opens a file: if one for this controller doesn't exist, falls back to a common one.

        Returns the file object opened as read-only in binary mode and unbuffered.
        """
        return open(self.path_with_common(name, controller), 'rb', buffering=0)
