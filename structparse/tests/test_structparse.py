import pytest

from .. import mystruct, types

def test_new():
    TestStruct = mystruct('TestStruct',
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

SubStruct = mystruct('SubStruct',
                      (types.Bytes(4),     'x'),
                      (types.Uint8,        'y'),
                      (types.PascalStr(5), 'z'))
Struct = mystruct('Struct',
                  (SubStruct,  'a'),
                  (types.Tail, 'b'))

s = Struct(SubStruct(b'quux', 0x47, 'foo'), b'kaleraby')
packed = b'quux' + b'\x47' + b'\x03foo\x00\x00' + b'kaleraby'

def test_pack():
    assert s.pack() == packed

def test_unpack():
    assert Struct.unpack_all(packed) == s
