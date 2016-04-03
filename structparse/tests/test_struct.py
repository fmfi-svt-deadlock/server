import pytest

from .. import struct, types


def test_new():
    TestStruct = struct('TestStruct',
                        (types.Uint8, 'john'),
                        (types.Uint8, 'paul'),
                        (types.Uint8, 'george'),
                        (types.Uint8, 'ringo'))
    def check(instance):
        assert (instance.john   == types.Uint8(12) and
                instance.paul   == types.Uint8(4)  and
                instance.george == types.Uint8(6)  and
                instance.ringo  == types.Uint8(0))
    check(TestStruct(12, 4, 6, 0))
    check(TestStruct(paul=4, george=6, john=12, ringo=0))
    check(TestStruct(12, 4, ringo=0, george=6))
    with pytest.raises(TypeError) as err:
        TestStruct(1, 2, 47)
    assert 'exactly 4' in str(err.value)
    with pytest.raises(TypeError) as err:
        TestStruct(12, 4, john=42, paul=47)
    assert 'arguments' in str(err.value)


@pytest.fixture
def Sample():
    return struct('Sample',
                  (types.Bytes(4),     'x'),
                  (types.Uint8,        'y'),
                  (types.PascalStr(5), 'z'))

@pytest.fixture
def Nested(Sample):
    return struct('Nested',
                  (Sample,     'a'),
                  (types.Tail, 'b'))

@pytest.fixture
def strct(Sample, Nested):
    return Nested(Sample(b'quux', 0x47, 'foo'), b'kaleraby')

@pytest.fixture
def packed():
    return b'quux' + b'\x47' + b'\x03foo\x00\x00' + b'kaleraby'


def test_pack(strct, packed):
    assert strct.pack() == packed

def test_unpack(Nested, packed, strct):
    assert Nested.unpack_all(packed) == strct
