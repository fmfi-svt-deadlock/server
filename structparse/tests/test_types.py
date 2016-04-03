import pytest

from .. import types
import enum

def test_construction():
    x = types.Uint8(47)
    y = types.Uint8(x)
    assert x == y

def test_tobytes():
    assert types._tobytes([97, 98, 99]) == b'abc'
    assert types._tobytes('mňau') == b'm\xc5\x88au'
    assert len(types._tobytes('mňau')) == 5

def test_eq():
    assert types.Uint8(47) == types.Uint8(47)
    assert types.Uint8(42) != types.Uint8(47)

def test_Uint8():
    assert types.Uint8(97).pack() == b'a'
    assert types.Uint8.unpack_from(b'abcd') == (types.Uint8(97), b'bcd')
    with pytest.raises(ValueError): types.Uint8(4742)

def test_Tail():
    assert types.Tail(b'an arbitrarily long whatever').pack() == b'an arbitrarily long whatever'
    assert types.Tail([97, 98, 99, 100]) == types.Tail(b'abcd')
    assert types.Tail.unpack(b'mrkva') == types.Tail(b'mrkva')

def test_Bytes():
    b4 = types.Bytes(4)
    assert repr(b4(b'abcd')) == "Bytes[4](b'abcd')"

    assert b4([97, 98, 99, 100]) == b4(b'abcd')

    with pytest.raises(ValueError): b4(b'abc')
    with pytest.raises(ValueError): b4(b'abcde')

    assert b4(b'abcd').pack() == b'abcd'
    assert b4.unpack_from(b'abcdefg') == (b4(b'abcd'), b'efg')
    with pytest.raises(ValueError): b4.unpack_from(b'abc')

def test_PascalStr():
    p6 = types.PascalStr(6)
    assert repr(p6(b'abcd')) == "PascalStr[6](b'abcd')"

    p6('Hello')  # n-1 bytes fit
    with pytest.raises(ValueError): p6('Hello!')  # n and more don't

    assert p6('hello').pack() == b'\x05hello'
    assert p6('hell').pack()  == b'\x04hell\x00'

    assert p6.unpack_from(b'\x03hel\x00\x00 world') == (p6(b'hel'), b' world')
    with pytest.raises(ValueError): p6.unpack_from(b'\x03hello world')
    with pytest.raises(ValueError): p6.unpack_from(b'\x47anything')

def test_hashable():
    assert hash(types.Uint8(47)) == hash(types.Uint8(47))
    assert hash(types.Uint8(47)) != hash(types.Uint8(42))
    assert hash(types.Bytes(2)([42,47])) != hash(types.Tail([42,47]))

def test_Enum_works():
    class T(types.Uint8, enum.Enum):
        A = 1
        B = 2
        Z = 255

    assert T(1) == T.A
    assert T.A.pack() == b'\x01'
    assert T.unpack(b'\xff') == T.Z
    with pytest.raises(ValueError): T(47)
    with pytest.raises(ValueError): T.unpack_from(b'\x47')

    with pytest.raises(ValueError):
        class T(types.Uint8, enum.Enum):
            X = 4742  # does not fit into 1 byte
