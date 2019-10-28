# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import unittest

from universa.types import PrivateKey, SimpleRole, HashSet


class TestHash(unittest.TestCase):
    def test(self):
        private_key = PrivateKey(size=2048)
        short_address = private_key.public_key.short_address
        role = SimpleRole('role', [short_address])
        x = role._invoke('getSimpleKeyAddresses')

        hashset = HashSet(id=x['id'])

        self.assertTrue(hashset[0].equals(short_address))


if __name__ == '__main__':
    unittest.main()
