import cbor

from common import tags, tag_names

from . import serializable

@serializable.cbor_serializable
class Record(dict):
    cbor_tag = tags.TYPE_RECORD

    def __init__(self, *args, **kwargs):
        d = dict(*args, **kwargs)
        super().__init__({tag_names.name(k): v for k, v in d.items()})

    def __getattr__(self, attr):
        if attr not in tag_names.tags_dict: raise AttributeError(attr)
        if attr not in self:
            raise ValueError('Required field {} not present in {}'.format(attr, self))
        return self[attr]

    def __setattr__(self, attr, value):
        if attr not in tag_names.tags_dict: return super().__setattr__(attr, value)
        self[attr] = value

    def __repr__(self):
        items = ['{}: {}'.format(k, v) for k, v in self.items()]
        return 'Record<{}>'.format(', '.join(items))

    def to_cbor(self):
        return [cbor.Tag(tag_names.value(k), serializable.cbor_encode(v)) for k, v in self.items()]

    @classmethod
    def from_cbor(cls, obj):
        rec = {}
        for t in obj:
            if t.tag in rec: raise ValueError('Tag {} present more than once'.format(t.tag))
            rec[t.tag] = t.value
        return cls(rec)
