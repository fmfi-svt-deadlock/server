import enum

from common import tags as T

@enum.unique
class MsgType(enum.IntEnum):
    PING     = T.MSG_PING
    XFER     = T.MSG_XFER
    ALOG     = T.MSG_ALOG
    ASK      = T.MSG_ASK
    ECHOTEST = T.MSG_ECHOTEST

@enum.unique
class ResponseStatus(enum.IntEnum):
    OK        = T.RESPONSE_OK
    ERR       = T.RESPONSE_ERR
    TRY_AGAIN = T.RESPONSE_TRY_AGAIN
