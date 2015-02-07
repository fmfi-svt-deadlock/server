from collections import namedtuple
from struct import Struct
from enum import Enum

PROTOCOL_VERSION = bytes([0x00,0x01])

class BadRequestError(Exception): pass

class MsgType(Enum):
    OPEN = 1

PacketHead = namedtuple('PacketHead', [
                        'protocol_version',
                        'controllerID',
                        'nonce',
])
PacketHead._struct = Struct('<2s6s18s')

RequestHead = namedtuple('RequestHead', [ 'msg_type' ])
RequestHead._struct = Struct('<B')

ReplyHead = namedtuple('ReplyHead', [ 'msg_type', 'status' ])
ReplyHead._struct = Struct('<BB')

def parse_into(cls, buf):
    """TODO doc"""
    assert hasattr(cls, '_struct') and isinstance(cls._struct, Struct)
    size = cls._struct.size
    head, tail = buf[:size], buf[size:]
    s = cls._struct.unpack(head)
    return cls(*s), tail

def fstring(buf):
    length, string = int(buf[0]), buf[1:]
    if not length <= len(string): raise BadRequestError()
    return string[:length]

def readpacket(buf):
    """Example usage."""
    p, payload = parse_into(PacketHead, buf)
    if not p.protocol_version == PROTOCOL_VERSION: raise BadRequestError
    print(p)
    # assume p is a request (usually this is determined by whether you are
    # server or client
    r, data = parse_into(RequestHead, payload)
    print(r)

    if MsgType(r.msg_type) == MsgType.OPEN:
        isic_id = fstring(data)
        print(isic_id)
    else:
        raise BadRequestError

if __name__ == '__main__':
    with open('./packet_example.bin', 'rb') as f:
        readpacket(f.read())
