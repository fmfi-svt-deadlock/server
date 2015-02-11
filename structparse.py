from collections import namedtuple
from struct import Struct
from enum import Enum

PROTOCOL_VERSION = bytes([0x00,0x01])
ENDIANITY        = '<'  # little

class BadMessageError(Exception): pass

def checkmsg(expression, err):
    if not expression: raise BadMessageError(err)

# pieces of struct format strings -- docs.python.org/3/library/struct.html
uint8_t = 'B'
bytes_t = lambda sz: '{}s'.format(sz)

def mystruct(name, fields, types):
    """Creates a namedtuple that can be packed to and unpacked from `bytes`.

    It simply attaches a `Struct` with the given format string.
    """
    cls = namedtuple(name, fields)
    cls._struct = Struct(ENDIANITY + ''.join(types))

    @classmethod
    def unpack_from(cls, buf):
        """Constructs a struct by unpacking the buffer.

        Returns the new instance and the rest of the buffer.
        """
        sz = cls._struct.size
        head, tail = buf[:sz], buf[sz:]
        return cls(*cls._struct.unpack(head)), tail

    def pack(self):
        """Returns itself packed as `bytes`."""
        return self._struct.pack(*self)

    cls.unpack_from = unpack_from
    cls.pack = pack
    return cls

class MsgType(Enum):
    OPEN = 1

class ReplyStatus(Enum):
    OK        = 0x01
    ERR       = 0x10
    TRY_AGAIN = 0x11
S = ReplyStatus

PacketHead = mystruct('PacketHead',
                     ['protocol_version', 'controllerID', 'nonce'      ],
                     [ bytes_t(2)       ,  bytes_t(6)   ,  bytes_t(18) ])

RequestHead = mystruct('RequestHead',
                      ['msg_type'],
                      [ uint8_t  ])

ReplyHead = mystruct('ReplyHead',
                    ['msg_type', 'status' ],
                    [ uint8_t  ,  uint8_t ])

def fstring(buf):
    length, string = int(buf[0]), buf[1:]
    checkmsg(length <= len(string), 'fstring length > buffer size')
    return string[:length]

process_request = {
    MsgType.OPEN:
        lambda data: ((S.OK if fstring(data) == 'Hello' else S.ERR), None),
}

def make_reply(packet_head, request_head, status, data):
    nnonce = bytearray(packet_head.nonce); nnonce[-1] |= 0x1
    p = PacketHead(protocol_version=PROTOCOL_VERSION,
                   controllerID=packet_head.controllerID,
                   nonce=nnonce)
    r = ReplyHead(msg_type=request_head.msg_type, status=status.value)
    return p.pack() + r.pack() + (data or bytes(0))

def handle_request(buf):
    p, payload = PacketHead.unpack_from(buf)
    checkmsg(p.protocol_version == PROTOCOL_VERSION, 'Invalid protocol version')
    checkmsg(p.nonce[-1] & 0x1 == 0, 'Last bit of request nonce must be 0')
    r, data = RequestHead.unpack_from(payload)
    try:
        t = MsgType(r.msg_type)
    except ValueError:
        raise BadMessageError('Unknown request type {}'.format(r.msg_type))
    status, data = process_request[t](data)
    return make_reply(p, r, status, data)

if __name__ == '__main__':
    with open('./packet_example.bin', 'rb') as f:
        reply = handle_request(f.read())
        print(reply)
