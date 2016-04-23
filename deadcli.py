#!/usr/bin/env python
"""deadcli.py: the Deadlock management commandline utility.

Run with --help for usage.
"""

import binascii
import os
import sys

import click
import nacl.secret
import nacl.utils
import records
import sqlalchemy.exc

import config

class myconfig:
    initdb_files = [os.path.join(os.path.dirname(__file__), f) for f in [
                    'sql/00-schema.sql',
                    'sql/01-materialize-rules.sql',
                    'sql/02-triggers.sql',
                    'sql/03-api-triggers.sql']]

def opendb():
    db = records.Database(config.db_url)
    db.db.execution_options(isolation_level='AUTOCOMMIT')
    return db

def die(msg):
    click.echo(msg, err=True)
    sys.exit(1)

@click.group()
def cli():
    """Manage Deadlock controller server."""
    pass

### CONTROLLER COMMANDS ############################################################################

@cli.group()
def controller():
    """Manage controllers."""
    pass

@controller.command('list')
def list_all():
    """List all controllers in the DB."""
    with opendb() as db:
        rows = db.query('SELECT mac, ip, p.name AS ap, last_seen, db_version, fw_version '
                        'FROM controller c LEFT OUTER JOIN accesspoint p ON p.controller_id = c.id '
                        'ORDER BY mac')
        click.echo(rows.dataset)

@controller.command()
@click.argument('mac')
def add(mac):
    """Add a controller to the DB, generating a key."""
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    with opendb() as db:
        try:
            db.query('INSERT INTO controller (mac, key) VALUES (:mac, :key)', mac=mac, key=key)
        except sqlalchemy.exc.IntegrityError as e:
            die(e.args[0])


@controller.command()
@click.argument('mac')
@click.argument('file', type=click.File('w'))
def writeconfig(mac, file):
    """Write controller configuration to file. This file must end up on the controller's SD card."""
    with opendb() as db:
        rows = db.query('SELECT mac, ip, key '
                        'FROM controller c LEFT OUTER JOIN accesspoint p ON c.id = p.controller_id '
                        'WHERE mac = :mac', mac=mac).all()
        # print(rows)
        if len(rows) != 1:
            die('Unknown controller MAC')
        r = rows[0]
        click.echo('mac = {}, ip = {}'.format(r.mac, r.ip))
        if r.mac and r.ip and r.key:
            file.write('{}\n{}\n{}\n'.format(
                r.mac, r.ip, binascii.hexlify(bytes(r.key)).decode('utf-8')))
        else:
            die('Config incomplete, giving up.')

### ACCESSPOINT COMMANDS ###########################################################################

@cli.group()
def accesspoint():
    """Manage accesspoints."""
    pass

@accesspoint.command('list')
def list_all():
    """List all accesspoints in the DB."""
    with opendb() as db:
        rows = db.query('SELECT ip, p.name, t.name AS type, c.mac AS controller '
                        'FROM accesspoint p LEFT OUTER JOIN aptype t ON p.type = t.id '
                        '     LEFT OUTER JOIN controller c ON p.controller_id = c.id '
                        'ORDER BY p.name')
        click.echo(rows.dataset)

@accesspoint.command()
@click.argument('ip')
@click.argument('name')
@click.argument('type')
def add(ip, name, type):
    """Add an accesspoint to the DB."""
    with opendb() as db:
        try:
            db.query('INSERT INTO aptype (name) SELECT :type '
                     'WHERE (NOT EXISTS (SELECT name FROM aptype WHERE name = :type))', type=type)
            db.query('INSERT INTO accesspoint (ip, name, type) VALUES (:ip, :name, '
                     '    (SELECT id FROM aptype WHERE name = :type))', ip=ip, name=name, type=type)
        except sqlalchemy.exc.IntegrityError as e:
            die(e.args[0])

@accesspoint.command()
@click.argument('ip')
@click.argument('mac')
def attach(ip, mac):
    """Mark an accesspoint as controlled by the given controller."""
    with opendb() as db:
        try:
            db.query('UPDATE accesspoint SET controller_id = '
                     '(SELECT id FROM controller WHERE mac = :mac) WHERE ip = :ip', mac=mac, ip=ip)
        except sqlalchemy.exc.IntegrityError as e:
            die(e.args[0])

### OTHER COMMANDS #################################################################################

@cli.command()
@click.option('--extra', multiple=True, type=click.Path(exists=True),
              help='apply this .sql file after initializing DB')
@click.confirmation_option(prompt='Really delete everything and make the DB like new?')
def newdb(extra):
    """Clear the DB to prepare for a new deployment.

    (Note for developers: use `make newdb_really_destroy_everything` for better error reporting.)
    """
    with opendb() as db:
        click.echo('dropping all tables')
        db.query('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
        for f in myconfig.initdb_files + list(extra):
            db.query_file(f)
            click.echo('applying file: {}'.format(f))

####################################################################################################

if __name__ == '__main__':
    cli()
