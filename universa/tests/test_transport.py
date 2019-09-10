# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import gc
import logging
import os
import subprocess
import time
import unittest

try:
    _FileNotFoundError = FileNotFoundError
except NameError:
    _FileNotFoundError = OSError

from streamexpect import ExpectTimeout

from universa.transport import transport
from universa.types import PrivateKey


logger = logging.getLogger()


class TestTransport(unittest.TestCase):
    TCP_SOCKET_HOST = '127.0.0.1'
    TCP_SOCKET_PORT = 59300
    UNIX_SOCKET_PATH = '/tmp/umi-socket-for-tests'

    umi_tcp_server = None
    umi_unix_server = None

    @classmethod
    def setUpClass(cls):
        try:
            os.remove(cls.UNIX_SOCKET_PATH)
        except _FileNotFoundError:
            pass

        cls.umi_tcp_server = subprocess.Popen(['umi', '--noexit', '--listen', 'tcp://{}:{}'.format(cls.TCP_SOCKET_HOST, cls.TCP_SOCKET_PORT)])
        cls.umi_unix_server = subprocess.Popen(['umi', '--noexit', '--listen', 'unix://{}'.format(cls.UNIX_SOCKET_PATH)])
        time.sleep(3)  # Wait a bit while both UMI servers start

    @classmethod
    def tearDownClass(cls):
        for attr in ('umi_tcp_server', 'umi_unix_server'):
            proc = getattr(cls, attr, None)
            if proc is not None:
                proc.terminate()

    def test_setupUMI(self):
        with self.assertRaises(ValueError):
            transport.setupUMI('pipe', 'veryrandombinaryname4242')
        transport.setupUMI('pipe', transport.DEFAULT_BINARY)

        # Test TCP and UNIX sockets
        i, config = 0, ('', {})
        configs = [
            ('tcp', {'host': self.TCP_SOCKET_HOST, 'port': self.TCP_SOCKET_PORT}),
            ('unix', {'path': self.UNIX_SOCKET_PATH}),
            ('pipe', {'path': transport.DEFAULT_BINARY}),
            ('tcp', {'host': self.TCP_SOCKET_HOST, 'port': self.TCP_SOCKET_PORT}),
        ]

        try:
            for i, config in enumerate(configs):
                method, connection_args = config
                transport.setupUMI(method, **connection_args)
                test = transport.test()
                self.assertEqual(test['result']['system'], 'UMI', 'connection to UMI failed')
                self.assertEqual(test['ref'], 0, 'invalid ref')
                time.sleep(1)
        except ExpectTimeout as e:
            logger.exception('UMI request failed with config %s: %s' % (i, str(config)))
            raise e

    def test_transport_GC(self):
        gc.enable()

        transport.setupUMI('pipe', transport.DEFAULT_BINARY)

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
