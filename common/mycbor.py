# TODO needs cleanup

import ast
import enum
import warnings
import ipaddress

import cbor
import cbor.tagmap
import yaml  # for prettyprinting / parsing hack

from constants import tags as mytags

Tag = cbor.Tag

def cbor_friendly(obj):
    """Coerce the given item into a more or less equivalent serializable type."""
    if isinstance(obj, list): return [cbor_friendly(x) for x in obj]
    if isinstance(obj, dict): return {k: cbor_friendly(v) for k, v in obj.items()}
    if isinstance(obj, memoryview): return obj.tobytes()
    if isinstance(obj, enum.Enum): return obj.value
    return obj

class Pretty:
    def __init__(self, tags):
        self.tags_dict = {tag: getattr(tags, tag) for tag in dir(tags) if not tag.startswith('_')}
        self.tags_reverse = {num: name for name, num in self.tags_dict.items()}

    def find_tag_name(self, tag):
        try:
            if isinstance(tag, enum.Enum): tag = tag.value
            if isinstance(tag, int): return self.tags_reverse[tag]
            if isinstance(tag, str):
                if tag not in self.tags_dict: raise KeyError
                return tag
            raise TypeError("Don't know how to convert {} to tag".format(type(tag)))
        except KeyError:
            raise ValueError('No such tag: {}'.format(tag))

    def find_tag_value(self, tag):
        if isinstance(tag, str) and not tag.isupper(): raise ValueError('Tags must be UPPERCASE')
        try:
            if isinstance(tag, enum.Enum): return tag.value
            if isinstance(tag, str): return self.tags_dict[tag]
            if isinstance(tag, int):
                if tag not in self.tags_reverse: raise KeyError
                return tag
            raise TypeError("Don't know how to convert {} to tag".format(type(tag)))
        except KeyError:
            raise ValueError('No such tag: {}'.format(tag))

    def show(self, data):
        def tr(item):
            if isinstance(item, Tag):
                return {'<' + self.find_tag_name(item.tag) + '>': tr(item.value)}
            if isinstance(item, dict):
                return {self.find_tag_name(k): tr(v) for k, v in item.items()}
            return item
        return yaml.dump(tr(data))

    def read(self, buf, tags=mytags):
        """Parses stuff formatted in a YAML syntax into tags and dicts. Format as follows:

        <TAGNAME>:
            FIELD1: 123
            FIELD2: hello
            FIELD3:
                <TAGGED_AGAIN>: [list, items]
            FIELD5:
                - everything
                - like
                - in
                - yaml
            BINARY: !!binary base64
        """
        def tr(item):
            if isinstance(item, str) and item.startswith('!'): return ast.literal_eval(item[1:])
            if isinstance(item, dict):
                # tag or record?
                if len(item) == 1:
                    key = list(item)[0]
                    if isinstance(key, int): return Tag(key, tr(item[key]))  # tag as int
                    if key.startswith('<') and key.endswith('>'):  # tag name
                        return Tag(find_tag_value(key[1:-1], tags), tr(item[key]))
                # if we've gotten here, it wasn't a tag
                return {self.find_tag_value(k): tr(v) for k, v in item.items()}
            return item
        return tr(yaml.load(buf))

def record_with_tags(tags, ident):
    """Returns a Record aware of the given tags namespace.

    Can be initialized with string tag names, and provides rec.TAG_NAME attribute access.
    """
    class Record:
        def __init__(self, *args, **kwargs):
            self._dict = dict(*args, **kwargs)
            for tag in self._dict:
                if not isinstance(tag, int):
                    raise TypeError("{} is not an integer tag".format(type(tag)))

        @staticmethod
        def to_cbor(rec):
            return [Tag(k, tagmapper.encode(v)) for k, v in rec._dict.items()]

        @classmethod
        def from_cbor(cls, obj):
            rec = {}
            for t in obj:
                if t.tag in rec: raise ValueError('Tag {} present more than once'.format(t.tag))
                rec[t.tag] = tagmapper.decode(t.value)
            return cls(rec)

    pretty = Pretty(tags)

    class RecordWithTags(Record, yaml.YAMLObject):
        def __init__(self, *args, **kwargs):
            def tr(item):
                if isinstance(item, dict):
                    return {pretty.find_tag_value(k): tr(v) for k, v in item.items()}
                return item
            super().__init__(tr(dict(*args, **kwargs)))

        def __getattr__(self, attr):
            if attr not in pretty.tags_dict: raise AttributeError(attr)
            print('in __getattr__, for', attr)
            tag = pretty.find_tag_value(attr)
            if tag not in self._dict:
                raise ValueError('Required field {} not present in {}'.format(tag, self))
            return self._dict[tag]

        def __setattr__(self, attr, value):
            if attr not in pretty.tags_dict: return super().__setattr__(attr, value)
            print('in __setattr__, for', attr)
            tag = pretty.find_tag_value(attr)
            self._dict[tag] = value

        def __repr__(self):
            items = ['{}: {}'.format(pretty.find_tag_name(k), v) for k, v in self._dict.items()]
            return '{}<{}>'.format(self.__class__.__name__, ', '.join(items))

        # @staticmethod
        # def to_yaml()

    RecordWithTags.__name__ = 'Record[{}]'.format(ident)
    return RecordWithTags

RecordDL = record_with_tags(mytags, 'DL')

class IPaddr(yaml.YAMLObject):
    """IPv4 or IPv6 address that can be stuffed into CBOR and YAML.

    Exists only because ipaddress.IPv{4,6}Address do not have a reasonable shared ancestor.
    """
    yaml_tag = '!IP'
    def __init__(self, addr):
        self.addr = ipaddress.ip_address(addr)

    @staticmethod
    def to_cbor(ip):
        return ip.packed

    @classmethod
    def from_cbor(cls, obj):
        return cls(obj)

    @classmethod
    def to_yaml(cls, dumper, ip):
        return dumper.represent_scalar(cls.yaml_tag, ip.exploded)

    @staticmethod
    def from_yaml(loader, node):
        value = loader.construct_scalar(node)
        return IPaddr(value)

    def __getattr__(self, attr):
        # proxy everything else to self.addr
        return getattr(self.addr, attr)

tagmapper = cbor.tagmap.TagMapper([
    cbor.tagmap.ClassTag(mytags.TYPE_RECORD, RecordDL, RecordDL.to_cbor, RecordDL.from_cbor),
    # cbor.tagmap.ClassTag(mytags.TYPE_IPADDR, IPaddr,   IPaddr.to_cbor,   IPaddr.from_cbor),
])

# for easier access
pretty = Pretty(tags=mytags)
dump = tagmapper.dumps
load = tagmapper.loads
