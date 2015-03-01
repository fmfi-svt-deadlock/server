from .controller_protocol import (checkmsg, MsgType, ResponseStatus, Response,
    response_packet_for, parse_packet, request_from_packet, BadMessageError)
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

def log_message(controllerID, mtype, indata, status):
    """TODO"""
    print(utils.bytes2mac(controllerID), mtype.name, indata, '->', status.name)

def log_bad_packet(buf, e):
    """TODO"""
    raise e

process_request = {
    MsgType.OPEN:
        lambda ctrl, data: ((ResponseStatus.OK if isic_id_repr(data) == b'Hello'
                             else ResponseStatus.ERR), b''),
}
assert set(MsgType) == set(process_request), 'Not all message types handled'

def handle_request(buf):
    try:
        packet = parse_packet(buf)
        key = get_key_for_mac(packet.controller_id)
        request = request_from_packet(packet, key)
        response_status, response_data = process_request[request.msg_type_e](
            packet.controller_id, request.tail)
        response = Response(request.msg_type_e.value, response_status.value)
        response.tail = response_data
        response_packet = response_packet_for(packet, response, key)
        log_message(packet.controller_id, request.msg_type_e, request.tail,
                    response_status)
        return response_packet.pack()
    except BadMessageError as e:
        log_bad_packet(buf, e)
