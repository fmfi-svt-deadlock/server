"""Handler for ECHOTEST requests: echo for testing purposes"""

from constants.enums import MsgType
from .defs import handles

@handles(MsgType.ECHOTEST)
def handle_echotest(controller, data, ctx):
    return data
