#!/usr/bin/env python3
"""Deadlock server runner."""

from deadserver import controller_server
import config

if __name__ == '__main__':
    app = controller_server.DeadServer(config)
    app.serve()
