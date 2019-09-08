# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import unittest

from universa.types import PrivateKey, PublicKey, KeyAddress


class TestCrypto(unittest.TestCase):
    def test(self):
        private = PrivateKey(size=2048)
        private_2 = PrivateKey(key=private.key)
        self.assertTrue(private.equals(private_2), 'equals for private keys failed')
        self.assertEqual(private.key, private_2.key, 'private keys are different')

        public = private.public_key
        public_3 = PublicKey(key=private.public_key.key)
        self.assertTrue(public_3.equals(public), 'equals for public keys failed')
        self.assertEqual(public_3.key, public.key, 'public keys are different')

        key_address = public.short_address
        self.assertFalse(key_address.is_long, 'short address should be `not is_long`')

        key_address_4 = KeyAddress(address=key_address.address)
        self.assertTrue(key_address_4.equals(key_address), 'equals for key addresses failed')
        self.assertTrue(key_address_4.is_matching_key_address(key_address), 'is_matching_key_address failed')
        self.assertEqual(key_address_4.address, key_address.address, 'key addresses are different')
        self.assertEqual(key_address_4.uaddress, key_address.uaddress, 'key addresses are different')

        key_address_5 = KeyAddress(uaddress=key_address.uaddress)
        self.assertTrue(key_address_5.equals(key_address), 'equals for key addresses failed')

        long_address = public.long_address
        self.assertTrue(long_address.is_long, 'long address should be is_long')


if __name__ == '__main__':
    unittest.main()
