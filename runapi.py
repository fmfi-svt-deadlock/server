#!/usr/bin/env python3
"""Deadlock HTTP API server runner."""

import logging.config

from deadapi import server
import config

if __name__ == '__main__':
    logging.config.dictConfig(config.logging_config)
    server.kill_default_logging()
    server.serve(config)
