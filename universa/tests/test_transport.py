# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import gc
import unittest

from universa.transport import transport
from universa.types import PrivateKey


class TestTransport(unittest.TestCase):

    def testSetup(self):
        with self.assertRaises(ValueError):
            transport.setupUMI('pipe', 'veryrandombinaryname4242')
        transport.setupUMI('pipe', 'umi')

    def test(self):
        gc.enable()

        self.assertEqual(len(transport.OBJECTS), 0, 'transport objects are not blank')

        key = PrivateKey(size=2048)
        self.assertEqual(len(transport.OBJECTS), 1, 'transport objects does not contains only one value')

        key2 = PrivateKey(size=2048)
        self.assertEqual(len(transport.OBJECTS), 2, 'transport objects does not contains only two values')

        # Create a key overriding previous one variable.
        # GarbageCollector should delete old object and kill it from transport (and UMI remote object).
        key2 = PrivateKey(size=2048)
        self.assertEqual(len(transport.OBJECTS), 2, 'transport objects does not contains only two values')

        # Create a key and don't save it to the variable. It should be deleted by UMI at once.
        PrivateKey(size=2048)
        self.assertEqual(len(transport.OBJECTS), 2, 'transport objects does not contains only two values')

        # Delete a local key object. It should be removed from UMI too.
        del key2
        self.assertEqual(len(transport.OBJECTS), 1, 'transport objects does not contains only one value')


if __name__ == '__main__':
    unittest.main()
