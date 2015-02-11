from collections import namedtuple
from struct import Struct
from enum import Enum

PROTOCOL_VERSION = bytes([0x00,0x01])
STRUCT_FORMAT    = '<'  # little-endian, no alignment (i.e. packed)

class BadMessageError(Exception): pass

def checkmsg(expression, err):
    if not expression: raise BadMessageError(err)

class t:
    """pieces of struct format strings: docs.python.org/3/library/struct.html"""
    uint8 = 'B'
    bytes = lambda sz: '{}s'.format(sz)

class MyStructBase:
    _struct = None

    @classmethod
    def set_struct(cls, formatstring):
        cls._struct = Struct(formatstring)

    @classmethod
    def unpack_from(cls, buf):
        """Constructs a new instance by unpacking the given buffer.

        Returns the new instance and the rest of the buffer.
        """
        sz = cls._struct.size
        head, tail = buf[:sz], buf[sz:]
        return cls(*cls._struct.unpack(head)), tail

    def pack(self):
        """Returns itself packed as `bytes`."""
        return self._struct.pack(*self)

def mystruct(name, fields, types):
    """Creates a namedtuple that can be packed to and unpacked from `bytes`."""
    class Cls(namedtuple(name, fields), MyStructBase): pass
    Cls.__name__ = name
    Cls.set_struct(STRUCT_FORMAT + ''.join(types))
    return Cls

class MsgType(Enum):
    OPEN = 1

class ReplyStatus(Enum):
    OK        = 0x01
    ERR       = 0x10
    TRY_AGAIN = 0x11
S = ReplyStatus

PacketHead = mystruct('PacketHead',
                     ['protocol_version', 'controllerID', 'nonce'      ],
                     [ t.bytes(2)       ,  t.bytes(6)   ,  t.bytes(18) ])

RequestHead = mystruct('RequestHead',
                      ['msg_type'],
                      [ t.uint8  ])

ReplyHead = mystruct('ReplyHead',
                    ['msg_type', 'status' ],
                    [ t.uint8  ,  t.uint8 ])

def fstring(buf):
    length, string = int(buf[0]), buf[1:]
    checkmsg(length <= len(string), 'fstring length > buffer size')
    return string[:length]

process_request = {
    MsgType.OPEN:
        lambda data: ((S.OK if fstring(data) == 'Hello' else S.ERR), None),
}

def make_reply_packet(packet_head, request_head, status, data):
    """Requires `packet_head` and `request_head` to be valid."""
    nnonce = bytearray(packet_head.nonce); nnonce[-1] |= 0x1
    p = PacketHead(protocol_version=PROTOCOL_VERSION,
                   controllerID=packet_head.controllerID,
                   nonce=nnonce)
    r = ReplyHead(msg_type=request_head.msg_type, status=status.value)
    return p.pack() + r.pack() + (data or bytes(0))

def parse_request_packet(buf):
    p, payload = PacketHead.unpack_from(buf)
    checkmsg(p.protocol_version == PROTOCOL_VERSION, 'Invalid protocol version')
    checkmsg(p.nonce[-1] & 0x1 == 0, 'Last bit of request nonce must be 0')
    r, data = RequestHead.unpack_from(payload)
    try:
        t = MsgType(r.msg_type)
    except ValueError:
        raise BadMessageError('Unknown request type {}'.format(r.msg_type))
    return p, r, t, data

def handle_request(buf):
    packet_head, request_head, request_type, indata = parse_request_packet(buf)
    status, outdata = process_request[request_type](indata)
    return make_reply_packet(packet_head, request_head, status, outdata)

if __name__ == '__main__':
    with open('./packet_example.bin', 'rb') as f:
        reply = handle_request(f.read())
        print(reply)
