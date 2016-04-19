#!/usr/bin/env python3
"""Deadlock HTTP API server runner."""

from deadapi import server
import config

if __name__ == '__main__':
    server.serve(config)
