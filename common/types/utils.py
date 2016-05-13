import yaml
from cbor import Tag

from .. import tag_names
from . import Record

def dict_to_records_and_tags(d):
    """Parses a dict into types.Record and cbor.Tag recursively.

    A dict with a single string key marked like <THIS> will be interpreted as a Tag, everything else
     as a Record.
    """
    def tr(item):
        if isinstance(item, dict):
            if len(item) == 1:
                key = list(item)[0]
                if hasattr(key, 'startswith') and key.startswith('<') and key.endswith('>'):  # tag
                    return Tag(tag_names.value(key[1:-1]), tr(item[key]))
            # if we've gotten here, it wasn't a tag, so a Record
            return Record({tag_names.name(k): tr(v) for k, v in item.items()})
        return item
    return tr(d)

def records_and_tags_to_dict(r):
    def tr(item):
        if isinstance(item, Tag): return {'<'+tag_names.name(item.tag)+'>': tr(item.value)}
        if isinstance(item, Record): return {k: tr(v) for k, v in item.items()}
        return item
    return tr(r)

def prettyprint(rec):
    return yaml.dump(records_and_tags_to_dict(rec))

def prettyread(buf):
    return dict_to_records_and_tags(yaml.load(buf))
