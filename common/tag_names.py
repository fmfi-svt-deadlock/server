from . import tags

tags_dict = {tag: getattr(tags, tag) for tag in dir(tags) if not tag.startswith('_')}
tags_reverse = {num: name for name, num in tags_dict.items()}

def name(tag):
    try:
        if isinstance(tag, int): return tags_reverse[tag]
        if isinstance(tag, str):
            if tag not in tags_dict: raise KeyError
            return tag
        raise TypeError("Don't know how to convert {} to tag".format(type(tag)))
    except KeyError:
        raise ValueError('No such tag: {}'.format(tag))

def value(tag):
    try:
        if isinstance(tag, str): return tags_dict[tag]
        if isinstance(tag, int):
            if tag not in tags_reverse: raise KeyError
            return tag
        raise TypeError("Don't know how to convert {} to tag".format(type(tag)))
    except KeyError:
        raise ValueError('No such tag: {}'.format(tag))
