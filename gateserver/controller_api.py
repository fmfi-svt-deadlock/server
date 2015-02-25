from .controller_protocol import (checkmsg, MsgType, ResponseStatus,
    make_response_for, parse_packet_head, parse_request, BadMessageError)
from . import db
from . import utils

def get_key_for_mac(mac):
    """Loads the key for this controller from the DB."""
    rs = db.exec_sql('SELECT key FROM controller WHERE id = %s',
                     (utils.bytes2mac(mac),), ret=True)
    checkmsg(len(rs) == 1, 'unknown controllerID')
    return bytes(rs[0]['key'])

def isic_id_repr(buf):
    """See https://github.com/fmfi-svt-gate/server/wiki/Controller-%E2%86%94-Server-Protocol#note-isic-ids-representation"""
    length, string = buf[0], buf[1:]
    checkmsg(length <= len(string), 'isic_id_repr length > buffer size')
    return string[:length]

process_request = {
    MsgType.OPEN:
        lambda data: ((ResponseStatus.OK if isic_id_repr(data) == b'Hello'
                       else ResponseStatus.ERR), None),
}
assert set(MsgType) == set(process_request), 'Not all message types handled'

def log_message(controllerID, mtype, indata, status):
    """TODO"""
    print(utils.bytes2mac(controllerID), mtype.name, indata, '->', status.name)

def log_bad_packet(buf, e):
    """TODO"""
    raise e

def handle_request(buf):
    try:
        packet_head, payload = parse_packet_head(buf)
        key = get_key_for_mac(packet_head.controllerID)
        request_head, mtype, indata = parse_request(packet_head, key, payload)
        status, outdata = process_request[mtype](indata)
        log_message(packet_head.controllerID, mtype, indata, status)
        return make_response_for(packet_head, request_head, key, status, outdata)
    except BadMessageError as e:
        log_bad_packet(buf, e)
