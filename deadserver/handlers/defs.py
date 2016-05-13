"""Provides functions for defining request handlers, such as the `handles(msg_type)` decorator."""

from ..protocol.constants import MsgType  # for easier access

_all_handlers = {}

def handles(msg_type):
    def decorator(fn):
        _all_handlers[msg_type] = fn
        fn.handles = msg_type
        return fn
    return decorator

def get_handler_for(msg_type):
    try:
        return _all_handlers[msg_type]
    except KeyError:
        raise ValueError('No handler for message type: {}'.format(msg_type))
