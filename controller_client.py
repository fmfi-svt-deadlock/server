"""Quick & dirty client (i.e. the controller end), used for manual testing of the server."""

import socket
import os
import sys

import records

import config
from deadserver.api import *
from deadserver.protocol import *

api = API(config=config, db=records.Database(config.db_url))

def msg(buf):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(buf, (config.udp_host, config.udp_port))
    return sock.recv(1024)

def send(id, msgtype, data):
    nonce = os.urandom(18)
    req = Request(msgtype.value, data)
    req_packet = make_packet(id, nonce, req, get_key=api.get_key)
    res_packet = msg(req_packet.pack())
    return parse_packet(Response, res_packet, get_key=api.get_key)

if __name__ == '__main__':
    mac, msgtype = sys.argv[1:]
    try:
        t = MsgType[msgtype.upper()]
    except KeyError:
        sys.exit('No such message type: '+msgtype)

    indata = sys.stdin.buffer.read()

    hdr, res = send(str2id(mac), t, indata)

    print(' * * * as {} sent request: {}'.format(mac, str(t)))
    print(indata)
    print(' * * * received response: {}'.format(str(t)))
    print(str(res.status))
    print(res.data)
