#!/usr/bin/env python3
"""Deadlock server runner."""

from deadserver import server
import config

if __name__ == '__main__':
    server.serve(config)
