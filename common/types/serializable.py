import enum

import cbor
import cbor.tagmap
import yaml

# TODO enums something something

### CBOR ###########################################################################################

def cbor_friendly(obj):
    """Coerce the given item into a more or less equivalent CBOR-serializable type."""
    if isinstance(obj, memoryview): return obj.tobytes()
    if isinstance(obj, enum.Enum): return obj.value
    return obj

_cbor_registered_types = []

def cbor_serializable(cls):
    if not hasattr(cls, 'cbor_tag'):
        raise ValueError('Cannot be made serializable without the cbor_tag property')
    _cbor_registered_types.append(cbor.tagmap.ClassTag(
        tag_number=cls.cbor_tag, class_type=cls,
        encode_function=lambda x: x.to_cbor(), decode_function=cls.from_cbor))
    return cls

def get_cbor_coder():
    # This is a function so that the tagmapper is created lazily -- so that things get registered
    # before tagmapper creation regardless of module load order. In this way, when you call
    # encode(stuff), stuff has certainly been registered in this version of tagmapper :D

    tagmapper = cbor.tagmap.TagMapper(_cbor_registered_types)
    #          __
    #     w  c(..)o   (
    #      \__(-)    __)
    #          /\   (        TODO remove this once mainstream fixed
    #         /(_)___)
    #         w /|
    #          | \
    #         m  m
    the_shitty_encode_that_doesnt_handle_Tag = tagmapper.encode
    def less_shitty_encode(item):
        if isinstance(item, cbor.Tag):
            return cbor.Tag(item.tag, less_shitty_encode(item.value))
        return cbor_friendly(the_shitty_encode_that_doesnt_handle_Tag(item))
    tagmapper.encode = less_shitty_encode

    the_shitty_decode_that_doesnt_handle_Tag = tagmapper.decode
    def less_shitty_decode(item):
        result = the_shitty_decode_that_doesnt_handle_Tag(item)
        if isinstance(result, cbor.Tag):
            return cbor.Tag(result.tag, less_shitty_decode(item.value))
        return result
    tagmapper.decode = less_shitty_decode
    return tagmapper

def cbor_encode(data):
    return get_cbor_coder().encode(data)

def cbor_decode(data):
    return get_cbor_coder().decode(data)

### YAML ###########################################################################################

def yaml_serializable(cls):
    if not hasattr(cls, 'yaml_tag'):
        raise ValueError('Cannot be made serializable without the yaml_tag property')
    yaml.add_representer(cls, lambda dumper, x: x.to_yaml(dumper))
    yaml.add_constructor(cls.yaml_tag, cls.from_yaml)
    return cls
