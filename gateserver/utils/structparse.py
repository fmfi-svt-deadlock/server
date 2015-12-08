from collections import namedtuple

def unzip(x): return zip(*x)

class _Type:
    """Defines a type that can be serialized and unserialized."""
    def __init__(self, pack, unpack):
        """
        pack:   data -> buffer
        unpack: buffer -> (parsed data, rest of the buffer)
        """
        self.pack   = pack
        self.unpack = unpack

def idf(x): return x

class t:
    """Defines a few useful types."""
    # Note: endianity must be handled once multi-byte numbers are needed
    tail  = _Type(idf, lambda buf: (buf, bytes([])))
    uint8 = _Type(lambda x: bytes([x]), lambda buf: (int(buf[0]), buf[1:]))
    bytes = lambda n: _Type(idf, lambda buf: (buf[:n], buf[n:]))
    #pstr  = lambda n: _Type(lambda s: [n]+bytes(s) if len(s) <= n else raise ValueError('error when encoding TODO'), lambda buf: (buf[1:buf[0]]), buf[n+1:])

class MyStructMixin:
    """Mixin providing the `pack` and `unpack` methods."""
    
    @classmethod
    def unpack(cls, data):
        """Constructs a new instance by unpacking the given buffer."""
        def _unpack(data):
            for t in cls._fieldtypes:
                val, data = t.unpack(data)
                yield val
            if len(data) > 0: raise ValueError('buffer size != struct size')

        return cls(*_unpack(data))

    def pack(self):
        """Returns itself packed as `bytes`."""
        return b''.join([ t.pack(x) for t,x in zip(self._fieldtypes, self) ])

def mystruct(name, *fields):
    """Creates a namedtuple that can be packed to and unpacked from `bytes`.

    `unpack(buf)` will raise `ValueError` if `len(buf)` doesn't exactly match
    the struct's size.
    """
    fieldtypes, fieldnames = unzip(fields)
    class Cls(namedtuple(name, fieldnames), MyStructMixin): pass
    Cls.__name__ = name
    Cls._fieldtypes = fieldtypes
    return Cls
