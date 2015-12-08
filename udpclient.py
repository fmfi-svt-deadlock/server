import config
from gateserver import db
from gateserver.controller_api import *
from gateserver.controller_protocol import *
from gateserver.utils import mac2bytes
import socket
import os
import sys

def msg(buf):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(buf, (config.udp_host, config.udp_port))
    return sock.recv(1024)

def request(mac, msgtype, data):
    key   = get_key_for_mac(mac)
    nonce = os.urandom(18)
    req = Request(msgtype.value, data)
    res = msg(make_packet(mac, key, nonce, req).pack())
    p = parse_packet(res)
    r = parse_response(p, key)
    return r

def prettyprint_reply(r):
    try:
        t = MsgType(r.msg_type)
        s = ResponseStatus(r.status)
    except ValueError:
        raise BadMessageError('Unknown type or status {}'.format(r.status))
    return '{} {}: {}'.format(t.name, s.name, r.data or '(no data)')

if __name__ == '__main__':
    mac, msgtype = sys.argv[1:]
    try:
        t = MsgType[msgtype.upper()]
    except KeyError:
        sys.exit('No such message type: '+msgtype)

    indata = sys.stdin.buffer.read()

    db.connect(config.db_url)
    reply = request(mac2bytes(mac), t, indata)
    print(prettyprint_reply(reply))
