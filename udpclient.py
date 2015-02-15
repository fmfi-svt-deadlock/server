import config
from gateserver import db
from gateserver.controller_api import *
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
    res = msg(make_packet(PacketHead(PROTOCOL_VERSION, mac, nonce),
                          RequestHead(msgtype.value),
                          key,
                          data))
    p, payload = parse_packet_head(res)
    r, t, data = parse_r(ReplyHead, p, key, payload)
    return p, r, t, data

def prettyprint_reply(p, r, t, data):
    try:
        s = ReplyStatus(r.status)
    except ValueError:
        raise BadMessageError('Unknown status {}'.format(r.status))
    return '{} {}: {}'.format(t.name, s.name, data or '(no data)')

if __name__ == '__main__':
    _, mac, msgtype = sys.argv
    try:
        t = MsgType[msgtype.upper()]
    except KeyError:
        sys.exit('No such message type: '+msgtype)

    indata = sys.stdin.buffer.read()

    db.connect(config.db_url)
    reply = request(mac2bytes(mac), t, indata)
    print(prettyprint_reply(*reply))
