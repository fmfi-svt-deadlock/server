#!/usr/bin/env python
"""deadcli.py: the Deadlock management commandline utility.

Run with --help for usage.
"""

import binascii
import os
import sys

import cbor
import click
import nacl.secret
import nacl.utils
import records
import sqlalchemy.exc

import config

from common.utils import conversions
from common import types
from common import types
from common.types.serializable import cbor_friendly, cbor_encode, cbor_decode

class myconfig:
    initdb_files = [os.path.join(os.path.dirname(__file__), f) for f in [
                    'sql/00-schema.sql',
                    'sql/01-materialize-rules.sql',
                    'sql/02-deadaux-triggers.sql',
                    'sql/03-api-triggers.sql',
                    ]]

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
        rows = db.query('''
            SELECT c.id, p.name AS ap, last_seen, db_version, fw_version
            FROM controller c LEFT OUTER JOIN accesspoint p ON p.controller = c.id
            ORDER BY p.name
            ''')
        click.echo(rows.dataset)

@controller.command('new')
@click.option('--write-config', default=None, type=click.File('wb'),
              help='Write controller config to file afterwards')
def new_controller(write_config):
    """Add a controller to the DB, generating a key."""
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    with opendb() as db:
        try:
            db.query('INSERT INTO controller (key) VALUES (:key)', key=key)
            new = db.query('SELECT id FROM controller WHERE key = :key', key=key)[0]['id']
            click.echo('Controller with id {} added.'.format(new))
            if write_config:
                writeconfig(new, write_config)
        except sqlalchemy.exc.IntegrityError as e:
            die(e.args[0])

# TODO extra key:value things, one day, possibly?
@controller.command()
@click.argument('id', type=int)
@click.argument('file', type=click.File('wb'))
def writeconfig(id, file):
    """Write controller configuration to file.

    This file must end up on the controller's SD card."""
    with opendb() as db:
        rows = db.query('SELECT key FROM controller c WHERE id = :id', id=id).all()
        if len(rows) != 1: die('Unknown controller ID')
        r = rows[0]
        conf = types.Record(CONFIG_ID=id, CONFIG_KEY='[not shown]')
        click.echo(types.utils.prettyprint(conf), nl=False)
        conf.CONFIG_KEY = cbor_friendly(r.key)
        file.write(cbor.dumps(cbor_encode(conf)))

@controller.command()
@click.argument('file', type=click.File('rb'))
def readconfig(file):
    """Print controller configuration in file."""
    conf = cbor_decode(cbor.loads(file.read()))
    for hidden in ('CONFIG_KEY', 'CONFIG_PRIVKEY'):
        if hidden in conf: conf[hidden] = '[not shown]'
    click.echo(types.utils.prettyprint(conf), nl=False)

### ACCESSPOINT COMMANDS ###########################################################################

@cli.group()
def accesspoint():
    """Manage accesspoints."""
    pass

@accesspoint.command('list')
def list_all():
    """List all accesspoints in the DB."""
    with opendb() as db:
        rows = db.query('''
            SELECT p.id, p.name, t.name AS type, controller, last_seen
            FROM accesspoint p
                 LEFT OUTER JOIN aptype t ON p.type = t.id
                 LEFT OUTER JOIN controller c ON p.controller = c.id
            ORDER BY type''')
        click.echo(rows.dataset)

@accesspoint.command()
@click.argument('name')
@click.argument('type')
def add(name, type):
    """Add an accesspoint to the DB."""
    with opendb() as db:
        try:
            db.query('''
                INSERT INTO aptype (name) SELECT :type
                WHERE (NOT EXISTS (SELECT name FROM aptype WHERE name = :type))
                ''', type=type)
            db.query('''
                INSERT INTO accesspoint (name, type)
                VALUES (:name, (SELECT id FROM aptype WHERE name = :type))
                ''', name=name, type=type)
        except sqlalchemy.exc.IntegrityError as e:
            die(e.args[0])

@accesspoint.command()
@click.argument('accesspoint')
@click.argument('controller')
def attach(accesspoint, controller):
    """Mark an accesspoint as controlled by the given controller."""
    with opendb() as db:
        try:  # accept name or ID
            ap_id = int(accesspoint)
        except ValueError:
            r = db.query('SELECT id FROM accesspoint WHERE name = :ap', ap=accesspoint).all()
            if not r: die('No such accesspoint: {}'.format(accesspoint))
            ap_id = r[0]['id']
        try:
            db.query('UPDATE accesspoint SET controller = :ctrl WHERE id = :ap',
                     ap=ap_id, ctrl=controller)
        except sqlalchemy.exc.IntegrityError as e:
            die(e.args[0])

### OTHER COMMANDS #################################################################################

@cli.command()
@click.option('--extra', multiple=True, type=click.Path(exists=True),
              help='apply this .sql file after initializing DB')
@click.option('--with-test-id/--without-test-id', default=True,
              help='add a controller and an accesspoint for testing purposes')
@click.confirmation_option(prompt='Really delete everything and make the DB like new?')
def newdb(extra, with_test_id):
    """Clear the DB to prepare for a new deployment.

    (Note for developers: use `make newdb_really_destroy_everything` for better error reporting.)
    """
    with opendb() as db:
        click.echo('dropping all tables')
        db.query('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
        for f in myconfig.initdb_files + list(extra):
            db.query_file(f)
            click.echo('applying file: {}'.format(f))
        if with_test_id:
            key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            db.query('INSERT INTO controller (id, key) VALUES (:id, :key)',
                     id=config.test_id, key=key)
            db.query("INSERT INTO accesspoint (id, name, controller) VALUES (:id, 'test', :id)",
                     id=config.test_id)


####################################################################################################

if __name__ == '__main__':
    cli()
