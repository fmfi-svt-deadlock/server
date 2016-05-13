"""Handler for ECHOTEST requests: echo for testing purposes"""

from .defs import handles, MsgType

@handles(MsgType.ECHOTEST)
def handle_echotest(controller, data, ctx):
    return data
