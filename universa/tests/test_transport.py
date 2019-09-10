# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import gc
import logging
import os
import subprocess
import time
import unittest

from streamexpect import ExpectTimeout

from universa.transport import transport
from universa.types import PrivateKey


logger = logging.getLogger()


class TestTransport(unittest.TestCase):
    TCP_SOCKET_HOST = '127.0.0.1'
    TCP_SOCKET_PORT = 59300
    UNIX_SOCKET_PATH = '/tmp/umi-socket-for-tests'

    def testSetup(self):
        with self.assertRaises(ValueError):
            transport.setupUMI('pipe', 'veryrandombinaryname4242')
        transport.setupUMI('pipe', transport.DEFAULT_BINARY)

        # Test TCP and UNIX sockets
        try:
            os.remove(self.UNIX_SOCKET_PATH)
        except FileNotFoundError:
            pass

        umi_tcp_server = subprocess.Popen(['umi', '--noexit', '--listen', 'tcp://{}:{}'.format(self.TCP_SOCKET_HOST, self.TCP_SOCKET_PORT)])
        umi_unix_server = subprocess.Popen(['umi', '--noexit', '--listen', 'unix://{}'.format(self.UNIX_SOCKET_PATH)])
        time.sleep(1)

        config = ('', {})
        configs = [
            ('tcp', {'host': self.TCP_SOCKET_HOST, 'port':self.TCP_SOCKET_PORT}),
            ('unix', {'path': self.UNIX_SOCKET_PATH}),
            ('pipe', {'path': transport.DEFAULT_BINARY}),
            ('tcp', {'host': self.TCP_SOCKET_HOST, 'port': self.TCP_SOCKET_PORT}),
        ]

        try:
            for config in configs:
                method, connection_args = config
                transport.setupUMI(method, **connection_args)
                test = transport.test()
                self.assertEqual(test['result']['system'], 'UMI', 'connection to UMI failed')
                self.assertEqual(test['ref'], 0, 'invalid ref')
                time.sleep(1)
        except ExpectTimeout as e:
            logger.exception('UMI request failed with config %s' % str(config))
            raise e
        finally:
            umi_tcp_server.kill()
            umi_unix_server.kill()

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
