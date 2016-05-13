#!/usr/bin/env python
"""Not much of an integration test, but serves as an "I didn't break everything" quick check."""

from datetime import datetime, timezone
from collections import namedtuple

import pytest
from records import Database

from controller import DumbController
from common.types import Record, IPaddr
from deadserver.protocol.utils import crypto_box_factory
from deadserver.protocol.constants import MsgType, ResponseStatus
from common.cfiles.filetypes import FileType

import config
CONTROLLER_ID = config.test_id

TIMEOUT = 3  # also allowed time difference; in seconds

@pytest.fixture(scope='module')
def controller():
    return DumbController(Record(
        CONFIG_ID=CONTROLLER_ID,
        CONFIG_SERVERS=[IPaddr(config.host)],
        CONFIG_SERVER_PORT=config.port,
    ), crypto_box_factory(Database(config.db_url))(CONTROLLER_ID))

@pytest.fixture()
def request(controller):
    return lambda msg_type, data: controller.request(msg_type=msg_type, data=data, timeout=TIMEOUT)

def test_echotest(request):
    status, re_data = request(MsgType.ECHOTEST, 'kalerab')
    assert status == ResponseStatus.OK
    assert re_data == 'kalerab'

def test_ping(request):
    status, re_data = request(MsgType.PING, Record(DB_VERSION=42, FW_VERSION=47, TIME=4742))
    assert status == ResponseStatus.OK
    deltat = datetime.now(timezone.utc) - datetime.fromtimestamp(re_data.TIME, timezone.utc)
    assert deltat.total_seconds() < TIMEOUT
    assert isinstance(re_data.DB_VERSION, int) and isinstance(re_data.FW_VERSION, int)

def test_xfer(request):
    status, re_data = request(MsgType.XFER, Record(
        FILEVERSION=0, FILETYPE=FileType.DB, OFFSET=0, LENGTH=47))  # v0 probably doesn't exist
    assert status == ResponseStatus.TRY_AGAIN

def test_ask(request):
    status, re_data = request(MsgType.ASK, Record(CARD_ID=b'a_long_id_that_probably_doesnt_exist'))
    assert status == ResponseStatus.OK
    assert re_data.ALLOWED is False

def test_alog(request):
    status, re_data = request(MsgType.ALOG, Record(CARD_ID=b'test', TIME=4742, ALLOWED=True))
    assert status == ResponseStatus.OK
    assert re_data is None

if __name__ == '__main__':
    pytest.cmdline.main()
