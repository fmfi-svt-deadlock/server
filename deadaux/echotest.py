"""Create a SMTPHandler logging config for echotest if you want to be emailed when things break."""

import logging
import sched
import socket

from records import Database

import config
from controller import DumbController
from common.types import Record, IPaddr
from deadserver.protocol.utils import crypto_box_factory
from deadserver.protocol.constants import MsgType, ResponseStatus

from .utils import fuzz

INITIAL_TIMEOUT = 3  # seconds; to give the server time to start up

log = logging.getLogger(__name__)

AS_CONTROLLER = config.test_id
myconfig = config.deadaux['echotest']

ctrl = DumbController(Record(
    CONFIG_ID=AS_CONTROLLER,
    CONFIG_SERVERS=[IPaddr(config.host)],
    CONFIG_SERVER_PORT=config.port,
), crypto_box_factory(Database(config.db_url))(AS_CONTROLLER))

scheduler = sched.scheduler()

def test(data):
    OK = True
    try:
        status, re_data = ctrl.request(MsgType.ECHOTEST, data, myconfig.get('timeout', 1))
        if status != ResponseStatus.OK:
            log.error('Response status was {}!'.format(status.name))
            OK = False
        if re_data != data:
            log.error('Response data mangled!')
            OK = False
        if not OK:
            log.error('Sent: {}'.format(data))
            log.error('Received: {} {}'.format(status.name, re_data))
        else:
            log.info('sent and received, all OK')
    except socket.timeout:
        log.error('Timed out, no response received!')
    except Exception:
        log.exception('Exception when sending data')

def run():
    scheduler.enter(myconfig.get('interval', 10), 1, run)
    test(fuzz(maxdepth=6))

def start(config):
    scheduler.enter(INITIAL_TIMEOUT, 1, run)
    scheduler.run(blocking=True)
