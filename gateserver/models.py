"""
The data models.
"""

from . import db

import nacl.raw as nacl

class Controller(db.StoredModelMixin):
    _table = 'controller'
    _attrs = { 'id'  : 'macaddr PRIMARY KEY',
               'ip'  : 'inet UNIQUE',
               'key' : 'bytea',
               'name': 'text',
             }

    def get(self, id=None, values={'id', 'ip', 'name'}):
        return super().get(id, values)

    def create(self, id, **kwargs):
        kwargs['key'] = nacl.randombytes(nacl.crypto_secretbox_KEYBYTES)
        super().create(id, **kwargs)
