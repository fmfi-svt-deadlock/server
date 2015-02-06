#!/usr/bin/env python3

import config
from gateserver import db

def db_create_tables():
    print('Creating DB tables...', end='')
    with open('./tables.sql', 'r') as f:
        if not db.conn: db.connect(config.db_url)
        for line in f:
            line = line.split('#')[0].strip()
            if line: db.exec_sql('CREATE TABLE IF NOT EXISTS ' + line)
    print(' OK')

def all():
    db_create_tables()

if __name__ == '__main__':
    all()
