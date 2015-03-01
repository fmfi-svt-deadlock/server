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

def send_request(mac, msgtype, data):
    key   = get_key_for_mac(mac)
    nonce = os.urandom(18)
    request = Request(msgtype.value); request.tail = data;
    request_packet = Packet(PROTOCOL_VERSION, mac, nonce);
    request_packet.tail = crypto_wrap(request_packet, key, request.pack());
    response_packet = parse_packet(msg(request_packet.pack()))
    return response_from_packet(response_packet, key)

def prettyprint_response(response):
    return '{} {}: {}'.format(response.msg_type_e.name, response.status_e.name,
                              response.tail or '(no data)')

if __name__ == '__main__':
    mac, msgtype = sys.argv[1:]
    try:
        t = MsgType[msgtype.upper()]
    except KeyError:
        sys.exit('No such message type: '+msgtype)

    indata = sys.stdin.buffer.read()

    db.connect(config.db_url)
    response = send_request(mac2bytes(mac), t, indata)
    print(prettyprint_response(response))
