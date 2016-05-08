def mac2bytes(s):
    return bytes.fromhex(s.replace(':', ''))

def bytes2mac(buf):
    return ':'.join('{:02x}'.format(x) for x in buf)
