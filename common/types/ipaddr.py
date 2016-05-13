import ipaddress

from common import tags

from . import serializable

@serializable.cbor_serializable
@serializable.yaml_serializable
class IPaddr:
    """IPv4 or IPv6 address that can be stuffed into CBOR and YAML."""
    yaml_tag = '!IP'
    cbor_tag = tags.TYPE_IPADDR

    def __init__(self, addr):
        self.addr = ipaddress.ip_address(addr)

    def to_cbor(self):
        return self.packed

    @classmethod
    def from_cbor(cls, ip):
        return cls(ip)

    def to_yaml(self, dumper):
        return dumper.represent_scalar(self.yaml_tag, self.exploded)

    @classmethod
    def from_yaml(cls, loader, node):
        value = loader.construct_scalar(node)
        return cls(value)

    def __repr__(self):
        return '{}<{}>'.format(self.__class__.__name__, self.exploded)

    def __getattr__(self, attr):
        # proxy everything else to self.addr
        return getattr(self.addr, attr)
