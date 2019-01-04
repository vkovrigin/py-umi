# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from universa.types import PrivateKey, SimpleRole, HashSet


def test():
    private_key = PrivateKey(size=2048)
    short_address = private_key.public_key.short_address
    role = SimpleRole('role', [short_address])
    x = role._invoke('getSimpleKeyAddresses')

    hashset = HashSet.get(x['id'])

    assert hashset.items[0].equals(short_address)
