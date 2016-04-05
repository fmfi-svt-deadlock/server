"""Handler for ECHOTEST requests."""

from ..protocol import MsgType, ResponseStatus

from .defs import handles

@handles(MsgType.ECHOTEST)
def handle_hello(controller_id, data, api):
    return ResponseStatus.OK, data
