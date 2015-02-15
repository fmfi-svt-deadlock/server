"""Various utility functions."""

def bytes2mac(mac):
    return ':'.join('{:02x}'.format(x) for x in mac)

def mac2bytes(s):
    return bytes.fromhex(s.replace(':', ''))

