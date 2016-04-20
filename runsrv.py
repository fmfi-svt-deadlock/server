#!/usr/bin/env python3
"""Deadlock server runner."""

import logging.config

from deadserver import server
import config

if __name__ == '__main__':
    logging.config.dictConfig(config.logging_config)
    server.serve(config)
