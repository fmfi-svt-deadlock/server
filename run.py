#!/usr/bin/env python3
"""Gate server runner."""

from gateserver import controller_api, http_api
import config

import psycopg2

def serve():
    controller_api.serve(config.controller_api)
    http_api.serve(config.http_api)

if __name__ == '__main__':
    serve()
