from . import controller_protocol as p
from . import db
from . import utils

def get_key_for_mac(mac):
    """Loads the key for this controller from the DB."""
    rs = db.exec_sql('SELECT key FROM controller WHERE id = %s',
                     (utils.bytes2mac(mac),), ret=True)
    p.checkmsg(len(rs) == 1, 'unknown controllerID')
    return bytes(rs[0]['key'])

def isic_id_repr(buf):
    """See https://github.com/fmfi-svt-gate/server/wiki/Controller-%E2%86%94-Server-Protocol#note-isic-ids-representation"""
    length, string = buf[0], buf[1:]
    p.checkmsg(length <= len(string), 'isic_id_repr length > buffer size')
    return string[:length]

process_request = {
    p.MsgType.OPEN:
        lambda data:
            ((p.S.OK if isic_id_repr(data) == b'Hello' else p.S.ERR), None),
}
assert set(p.MsgType) == set(process_request), 'Not all message types handled'

def log_message(controllerID, mtype, indata, status):
    """TODO"""
    print(utils.bytes2mac(controllerID), mtype.name, indata, '->', status.name)

def log_bad_packet(buf, e):
    """TODO"""
    raise e

def handle_request(buf):
    try:
        packet_head, payload = p.parse_packet_head(buf)
        key = get_key_for_mac(packet_head.controllerID)
        request_head, mtype, indata = p.parse_r(
                p.RequestHead, packet_head, key, payload)
        status, outdata = process_request[mtype](indata)
        log_message(packet_head.controllerID, mtype, indata, status)
        return p.make_reply_for(packet_head, request_head, key, status, outdata)
    except p.BadMessageError as e:
        log_bad_packet(buf, e)
