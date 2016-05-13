import os
import random

def fuzz(maxdepth=8):
    """Generate a random data structure (nesting lists, dicts, ints and bytestrings).

    Useful for fuzz testing.
    """
    MAX_LIST_LENGTH   = 8
    MAX_STRING_LENGTH = 256
    MAX_DICT_SIZE     = 8
    LOTS              = 1e47  # why not :D

    def _list(maxdepth):
        return [stuff(maxdepth - 1) for _ in range(random.randint(0, MAX_LIST_LENGTH))]

    def _int(_):
        return random.randint(-LOTS, LOTS)

    def _string(_):
        return os.urandom(random.randint(0, MAX_STRING_LENGTH))

    def _dict(maxdepth):
        return {_string(0): stuff(maxdepth - 1) for _ in range(random.randint(0, MAX_DICT_SIZE))}

    def stuff(maxdepth):
        fn = random.choice(([_list, _dict, stuff] if maxdepth > 0 else []) + [_int])
        return fn(maxdepth - 1)

    return stuff(maxdepth)
