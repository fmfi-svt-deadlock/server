"""Defines useful simple types for structparse."""

from .structdef import Type

class _SimpleType(Type):
    def __init__(self, x):
        if x.__class__ is self.__class__: self.__val = x.val
        else:
            self._validate(x)
            self.__val = x

    @property
    def val(self):
        return self.__val

    def pack(self):
        return bytes(self._pack())

    @classmethod
    def unpack_from(cls, buf):
        val, rest = cls._unpack_from(buf)
        return cls(val), rest

    def _validate(self, input):
        """No-op if the input is valid or raises exception if invalid."""
        pass

    def _pack(self):
        return self.val

    def __eq__(self, other):
        return self.val == other.val

    def __hash__(self):
        return hash(self.__class__.__name__) ^ hash(self.val)

    def __repr__(self):
        return self.__class__.__name__+'('+repr(self.val)+')'


def _tobytes(x):
    if isinstance(x, _SimpleType): return bytes(x.val)
    if isinstance(x, str): return bytes(x, 'utf8')
    return bytes(x)


class Uint8(_SimpleType):
    @staticmethod
    def _unpack_from(buf):
        return int(buf[0]), buf[1:]

    @staticmethod
    def _validate(x):
        if not 0 <= x <= 0xff: raise ValueError('{} is not a 1-byte unsigned int'.format(x))

    def _pack(self):
        return [self.val]


class _BytesLike(_SimpleType):
    def __init__(self, arg):
        super().__init__(_tobytes(arg))


class Tail(_BytesLike):
    @staticmethod
    def _unpack_from(buf):
        return buf, b''


def Bytes(n):
    class Cls(_BytesLike):
        @staticmethod
        def _validate(arg):
            if len(arg) != n:
                raise ValueError('{} is not {} bytes'.format(arg, n))
            return bytes(arg)

        @staticmethod
        def _unpack_from(buf):
            return buf[:n], buf[n:]

    Cls.__name__ = 'Bytes[{}]'.format(n)
    return Cls


def PascalStr(n):
    """A fixed-length "Pascal string" -- byte 0 is length, the rest is null-padded string content.

    Note that n is the number of bytes in the resulting binary representation, so at most n-1 bytes
    fit inside.
    """
    assert n >= 1, 'Cannot create PascalStr that can fit -1 bytes'
    assert n-1 <= 0xff, 'Max length of PascalStr must fit into 1 byte'
    class Cls(_BytesLike):
        @staticmethod
        def _validate(arg):
            if len(arg) > n-1:
                raise ValueError('string too long (n = {})'.format(n))

        @staticmethod
        def _unpack_from(buf):
            buf, tail = buf[:n], buf[n:]
            s, data = buf[0], buf[1:]
            if s > n-1: raise ValueError('packed string too long (n-1 = {}, s = {})'.format(n-1, s))
            result, padding = data[:s], data[s:]
            if not all([b == 0 for b in padding]): raise ValueError('packed string not null-padded')
            return result, tail

        def _pack(self):
            padding = n-1 - len(self.val)
            return bytes([len(self.val)]) + self.val + b'\0'*padding

    Cls.__name__ = 'PascalStr[{}]'.format(n)
    return Cls


# Note: if you are looking for Enum, this Just Works with Python's enum.Enum:
#
#   class T(types.Uint8, enum.Enum):
#       A = 1
#       B = 2
#       Z = 255
