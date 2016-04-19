#!/usr/bin/env python3
"""Gate server runner."""

from gateserver import db, controller_server
import config
import logging

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(ip)s %(message)s %(status)s',
    datefmt='%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    try:
        db.connect(config.db_url)
        controller_server.serve(config)
    except (SystemExit, KeyboardInterrupt):
        logging.shutdown()
