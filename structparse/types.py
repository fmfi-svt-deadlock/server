"""Defines default types for structparse."""

from . import Type

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
    def unpack(cls, buf):
        val, rest = cls._unpack(buf)
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
    def _unpack(buf):
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
    def _unpack(buf):
        return buf, b''

def Bytes(n):
    class Cls(_BytesLike):
        @staticmethod
        def _validate(arg):
            if len(arg) != n:
                raise ValueError('{} is not {} bytes'.format(arg, n))
            return bytes(arg)

        @staticmethod
        def _unpack(buf):
            return buf[:n], buf[n:]

    Cls.__name__ = 'Bytes[{}]'.format(n)
    return Cls

def PascalStr(n):
    class Cls(_BytesLike):
        @staticmethod
        def _validate(arg):
            if len(arg) > n:
                raise ValueError('string too long (n = {})'.format(n))

        @staticmethod
        def _unpack(buf):
            if buf[0] > n: raise ValueError('packed string too long (n = {}, buf[0] = {})'.format(n, buf[0]))
            b, e = buf[0]+1, n+1
            if buf[b:e] != b'\0'*(e-b): raise ValueError('packed string not null-padded')
            return buf[1:b], buf[e:]

        def _pack(self):
            padding = n - len(self.val)
            return bytes([len(self.val)]) + self.val + b'\0'*padding

    Cls.__name__ = 'PascalStr[{}]'.format(n)
    return Cls
