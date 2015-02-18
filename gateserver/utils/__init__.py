"""Various utility functions."""

def bytes2mac(mac):
    return ':'.join('{:02x}'.format(x) for x in mac)

def mac2bytes(s):
    return bytes.fromhex(s.replace(':', ''))

def unzip(lst):
    return zip(*lst)  # yay :D
