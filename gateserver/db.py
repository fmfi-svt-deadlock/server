"""Manages the DB -- holds the connection and provides CRUD primitives."""

import config

import psycopg2

db = psycopg2.connect(config.db_url)
db.autocommit=True

def exec_sql(query, args=(), ret=False):
    """Execute the query, returning the result as a list if `ret` is set."""
    with db.cursor() as cur:
        cur.execute(query, args)
        if ret: return cur.fetchall()

################################################################################

def unzip(lst):
    return zip(*lst)

class StoredModelMixin:
    """Defines CRUD methods for an object.

    The object must define `_table` -- the table name, and `_attrs`: a dict of
    name: type for the column types.

    String interpolation is used with `_table` and `_attrs`, therefore THESE
    PROPERTIES MUST NEVER BE SET WITH USER-SUPPLIED DATA.
    """

    def __init__(self):
        cols = ','.join([ k+' '+v for k, v in self._attrs.items() ])
        exec_sql("CREATE TABLE IF NOT EXISTS {} ({})".format(self._table, cols))

    def get(self, id=None, cols=None):
        if cols == None: cols = self._attrs
        assert(set(cols) <= set(self._attrs))
        cols = list(cols)
        q = 'SELECT {} FROM {}'.format(','.join(cols), self._table)
        if id: q += ' WHERE id = %s'
        r = [ dict(zip(cols, s)) for s in exec_sql(q, (id,), ret=True) ]
        if id:
            if r == []: return None
            else: return r[0]
        else: return r

    def create(self, id, **args):
        assert(set(args) <= set(self._attrs))
        args['id'] = id
        keys, values = unzip(list(args.items()))
        ks = ','.join(keys); vs = ','.join(['%s']*len(values))
        exec_sql('INSERT INTO {} ({}) VALUES ({})'.format(self._table, ks, vs),
                  values)

    def delete(self, id):
        exec_sql('DELETE FROM {} WHERE id = %s'.format(self._table), (id,))
