#!/usr/bin/env python3
"""Gate server runner."""

from gateserver import db, controller_api, http_api
import config

def serve():
    db.connect(config.db_url)
    controller_api.serve(config.controller_api)
    http_api.serve(config.http_api)

if __name__ == '__main__':
    serve()
