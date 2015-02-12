#!/usr/bin/env python3
"""Gate server runner."""

from gateserver import db, controller_server
import config

if __name__ == '__main__':
    try:
        db.connect(config.db_url)
        controller_server.serve(config)
    except (SystemExit, KeyboardInterrupt):
        pass
