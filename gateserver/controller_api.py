from .controller_protocol import *
from . import db
from . import utils

def get_key_for_mac(mac):
    """Loads the key for this controller from the DB."""
    rs = db.exec_sql('SELECT key FROM controller WHERE id = %s',
                     (utils.bytes2mac(mac),), ret=True)
    checkmsg(len(rs) == 1, 'unknown controllerID', mac)
    return rs[0]['key'].tobytes()

def fstring(buf):
    """See https://github.com/fmfi-svt-gate/server/wiki/Controller-%E2%86%94-Server-Protocol#note-isic-ids-representation"""
    length, string = int(buf[0]), buf[1:]
    checkmsg(length <= len(string), 'fstring length > buffer size', buf)
    return string[:length]

process_request = {
    MsgType.OPEN:
        lambda data: ((S.OK if fstring(data) == b'Hello' else S.ERR), None),
}
assert set(MsgType) == set(process_request), 'Not all message types are handled'

def log_message(controller_id, mtype, data, status):
    """Saves the request and the response status into the DB."""
    mtype, status = mtype.name, status.name
    controller_id = utils.bytes2mac(controller_id)
    db.exec_sql('INSERT INTO log_messages   (controller_id, mtype, data, status)'
                'VALUES (%s, %s, %s, %s)',  (controller_id, mtype, data, status))

def log_bad_packet(error, data):
    """Saves the bad packet into the DB."""
    db.exec_sql('INSERT INTO log_badpackets (error, data)'
                'VALUES (%s, %s)',          (error, data))
    print(utils.nowstr(), 'bad packet received:', error)

def handle_request(buf):
    try:
        pkt_head, payload = parse_packet_head(buf)
        key = get_key_for_mac(pkt_head.controllerID)
        req_head, mtype, indata = parse_r(RequestHead, pkt_head, key, payload)
        status, outdata = process_request[mtype](indata)
        log_message(pkt_head.controllerID, mtype, indata, status)
        return make_reply_for(pkt_head, req_head, key, status, outdata)
    except BadMessageError as e:
        log_bad_packet(e.message, e.data)
