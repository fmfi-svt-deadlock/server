"""Provides helpers for conveniently defining request handlers."""

import functools

from .. import protocol

def unpack_indata_as(struct):
    """Decorator to first unpack the request data buffer into the given struct."""
    def decorator(fn):
        @functools.wraps(fn)
        def decorated(controller_id, indata, api):
            try:
                unpacked = struct.unpack(indata)
            except ValueError as e:
                raise protocol.BadMessageError('parsing data failed') from e
            return fn(controller_id, unpacked, api)
        return decorated
    return decorator

def pack_outdata(fn):
    """Decorator to pack the structured response data into bytes."""
    @functools.wraps(fn)
    def decorated(controller_id, indata, api):
        status, outdata = fn(controller_id, indata, api)
        return status, (outdata.pack() if outdata else None)
    return decorated
