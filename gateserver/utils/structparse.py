from collections import namedtuple
from struct import Struct
from enum import Enum
from . import unzip

ENDIANITY = '<'  # little-endian, no alignment (i.e. packed)

class t:
    """pieces of struct format strings: docs.python.org/3/library/struct.html"""
    uint8 = 'B'
    bytes = lambda sz: '{}s'.format(sz)

class MyStructMixin:
    _struct = None

    @classmethod
    def unpack(cls, buf):
        """Constructs a new instance by unpacking the (whole) given buffer.

        The buffer size must be equal to the corresponding C struct size.
        """
        return cls(*cls._struct.unpack(head)), tail

    @classmethod
    def unpack_with_tail(cls, buf):
        """Constructs a new instance by unpacking the head of the given buffer.

        The buffer size may be greater than the corresponding C struct size; the
        rest of the buffer will be available in the `tail` member (as `bytes`).
        """
        sz = cls._struct.size
        head, tail = buf[:sz], buf[sz:]
        r = cls(*cls._struct.unpack(head))
        r.tail = tail
        return r

    def pack(self):
        """Returns itself packed as `bytes`, including the tail if it exists."""
        return self._struct.pack(*self) + getattr(self, 'tail', b'')

def mystruct(name, *fields):
    """Creates a namedtuple that can be packed to and unpacked from `bytes`."""
    fieldtypes, fieldnames = unzip(fields)
    class Cls(namedtuple(name, fieldnames), MyStructMixin): pass
    Cls.__name__ = name
    Cls._struct = Struct(ENDIANITY + ''.join(fieldtypes))
    return Cls
