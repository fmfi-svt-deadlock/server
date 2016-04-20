"""Controller files: opens files meant to be transferred to controllers via the XFER message."""

import errno
import os

from deadserver import protocol

COMMON_DIR = 'common'

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
    def __init__(self, path):
        self.path = path

    def _real_name(self, controller_id, name):
        if os.sep in name: raise ValueError('file name may not contain directories')
        for_dir = protocol.show_id(controller_id) if controller_id else COMMON_DIR
        return os.path.join(self.path, for_dir, name)

    def open(self, name, for_id=None, *args, **kwargs):
        """Opens files for the given controller.

        `for_id` can be either a controller ID, or `None` for files common to all controllers.

        See also `find_as`.
        """
        real_name = self._real_name(for_id, name)
        mkdirnx(os.path.dirname(real_name))
        return open(real_name, *args, **kwargs)

    def find_for(self, controller_id, name):
        """Finds a file: if one for this controller doesn't exist, falls back to a common one.

        Returns the file object opened as read-only in binary mode and unbuffered.
        """
        real_name = self._real_name(controller_id, name)
        if not os.path.exists(real_name): real_name = self._real_name(None, name)
        if not os.path.exists(real_name): raise ValueError('file not found')
        return open(real_name, 'rb', buffering=0)

    def ls_for(self, controller_id):
        """Lists files available for this controller. Pass `None` to list common ones."""
        real_dir = self._real_name(controller_id, '')
        try:
            return os.listdir(real_dir)
        except FileNotFoundError:
            return []
