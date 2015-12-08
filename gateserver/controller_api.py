from .controller_protocol import (checkmsg, MsgType, ResponseStatus,
    parse_packet, parse_request, make_response_packet_for, BadMessageError)
from . import db
from . import utils

def get_key_for_mac(mac):
    """Loads the key for this controller from the DB."""
    rs = db.exec_sql('SELECT key FROM controller WHERE id = %s',
                     (utils.bytes2mac(mac),), ret=True)
    checkmsg(len(rs) == 1, 'unknown controller_id')
    return bytes(rs[0]['key'])

def isic_id_repr(buf):
    """See https://github.com/fmfi-svt-gate/server/wiki/Controller-%E2%86%94-Server-Protocol#note-isic-ids-representation"""
    length, string = buf[0], buf[1:]
    checkmsg(length <= len(string), 'isic_id_repr length > buffer size')
    return string[:length]

# Note: once this function does something useful, it will be defined elsewhere
def handle_open(data):
    s = ResponseStatus.OK if isic_id_repr(data) == b'Hello' else ResponseStatus.ERR
    return s, None

process_request = {
    MsgType.OPEN: handle_open,
}
assert set(MsgType) == set(process_request), 'Not all message types handled'

def log_message(controller_id, request, status):
    """TODO"""
    # print(utils.bytes2mac(controller_id), mtype.name, indata, '->', status.name)
    print(utils.bytes2mac(controller_id), request, '->', status.name)

def log_bad_packet(buf, e):
    """TODO"""
    raise e

def handle_packet(buf):
    try:
        in_packet = parse_packet(buf)
        key = get_key_for_mac(in_packet.controller_id)
        request = parse_request(in_packet, key)
        status, outdata = process_request[MsgType(request.msg_type)](request.data)
        out_packet = make_response_packet_for(in_packet, key, request, status, outdata)
        log_message(in_packet.controller_id, request, status)
        return out_packet.pack()
    except BadMessageError as e:
        log_bad_packet(buf, e)
