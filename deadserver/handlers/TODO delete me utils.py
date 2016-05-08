"""Provides helpers for conveniently defining request handlers."""

import functools

from common.utils.cbor import record

from .. import protocol

def deserialize_in(fn):
    """Decorator to first deserialize the request data as a CBOR record"""
    @functools.wraps(fn)
    def decorated(controller, indata, api):
        try:
            parsed = record.load(indata)
        except ValueError:
            raise protocol.BadMessageError('parsing data failed') from e
        return fn(controller, parsed, api)
    return decorated

def serialize_out(fn):
    """Decorator to serialize the response data. It must be a CBOR record."""
    @functools.wraps(fn)
    def decorated(controller, indata, api):
        return record.dump_coerce(fn(controller, indata, api))
    return decorated
