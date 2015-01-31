"""Manages the DB -- holds the connection and provides CRUD primitives."""

import config

import psycopg2

db = psycopg2.connect(config.db_url)
db.autocommit=True

def exec_sql(query, args=(), ret=True):
    """Execute the query, returning the result as a list if `ret` is set."""
    with db.cursor() as cur:
        cur.execute(query, args)
        if ret: return cur.fetchall()

################################################################################

def dict_intersect(d, f):
    """Only keeps those keys of d which are present in f. Values stay intact."""
    r = {}
    for k, v in d.items():
        if k in f:
            r[k] = v
    return r

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
        exec_sql("CREATE TABLE IF NOT EXISTS {} ({})".format(self._table, cols),
                 ret=False)

    def get(self, id=None, values=None):
        if values == None: values = self._attrs
        cols = list(dict_intersect(self._attrs, values).keys())
        vs = ','.join(cols)
        w = 'WHERE id = %s' if id else ''
        r = exec_sql('SELECT {} FROM {} {}'.format(vs, self._table, w), (id,))
        rr = [ dict(zip(cols, s)) for s in r ]  # {key: value} instead of tuples
        if id:
            if rr == []: return None
            else: return rr[0]
        else: return rr

    def create(self, id, **kwargs):
        args = dict_intersect(kwargs, self._attrs)
        args['id'] = id
        keys, values = unzip(list(args.items()))
        ks = ','.join(keys); vs = ','.join(['%s']*len(values))

        exec_sql('INSERT INTO {} ({}) VALUES ({})'.format(self._table, ks, vs),
                  values, ret=False)

    def delete(self, id):
        exec_sql('DELETE FROM {} WHERE id = %s'.format(self._table), (id,),
                 ret=False)
