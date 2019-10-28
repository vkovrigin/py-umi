# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import os
import pexpect
import socket
import streamexpect
import weakref

from universa import logging
from universa import exceptions

logger = logging.getLogger()


class Transport(object):
    DEFAULT_CONNECTION_METHOD = 'pipe'
    DEFAULT_BINARY = 'umi'
    DEFAULT_CONNECTION_CONFIG = (DEFAULT_CONNECTION_METHOD, DEFAULT_BINARY)
    WINDOW = 1024 * 1024 * 5

    OBJECTS = {}

    method = DEFAULT_CONNECTION_METHOD
    __instance = None
    __proc = None

    def __init__(self, serial=0):
        if Transport.__instance is not None:
            raise Exception('Universa Transport is a singleton.')

        Transport.__instance = self
        self.OBJECTS = weakref.WeakValueDictionary()
        self.serial = max(serial, 0)

    def __del__(self):
        logger.debug('Cleaning')
        if self.__proc is not None:
            self.drop_objects(drop_all=True)
            self.__proc.close()

    @classmethod
    def setupUMI(cls, method, path=None, host=None, port=None, serial=0):
        """Configure Python to use a specific UMI connection.

        :param method: one of `'pipe'`, `'tcp'` or `'unix'`.
            If `path='pipe'`, you must provide the `path` argument with the path to the UMI executable;
            may be in $PATH.
            If `path='tcp'`, you must provide the `host` and `port` arguments of the UMI TCP server.
            If `path='unix'`, you must provide the `path` argument to connect to the UMI TCP server.
        :return: the transport (pexpect) instance
        :raises ValueError: if the arguments are improperly provided;
            if UMI executable is not available or reachable.
        """
        if method == 'pipe':
            if not path:
                raise ValueError('In "pipe" mode, you should provide non-empty "path" for UMI binary!')
            builder = lambda: cls.__make_pipe_transport(path)
        elif method == 'tcp':
            if not host or not port:
                raise ValueError('In "tcp" mode, you should provide non-empty "host" and "port" for UMI TCP socket!')
            builder = lambda: cls.__make_tcp_transport(host, port)
        elif method == 'unix':
            if not path:
                raise ValueError('In "unix" mode, you should provide non-empty "path" for UMI Unix socket!')
            builder = lambda: cls.__make_unix_transport(path)
        else:
            raise ValueError('Unsupported method {}'.format(method))

        # We have a `builder` defined here.
        # Do we have a running transport already?
        if cls.__proc is not None:
            try:
                cls.__instance.drop_objects(drop_all=True)
                cls.__proc.close()
            except OSError:
                pass

        cls.__proc = builder()
        cls.method = method
        transport.serial = max(serial, 0)

    @staticmethod
    def __make_pipe_transport(binary_path):
        try:
            return pexpect.spawn(binary_path, timeout=None, maxread=Transport.WINDOW)
        except pexpect.exceptions.ExceptionPexpect as e:
            if e.value.startswith('The command was not found or was not executable:'):
                raise ValueError('UMI executable you have chosen is not available at the requested path (or in $PATH).')
            else:
                raise

    @staticmethod
    def __make_tcp_transport(host, port):
        try:
            sock = socket.create_connection((host, port))
        except ConnectionRefusedError:
            raise ConnectionRefusedError('UMI refused the connection at tcp://%s:%s.' % (host, port))
        return streamexpect.wrap(sock, window=Transport.WINDOW, close_stream=False)

    @staticmethod
    def __make_unix_transport(socket_path):
        socket_path = os.path.abspath(socket_path)
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(socket_path)
        except ConnectionRefusedError:
            raise ConnectionRefusedError('UMI refused the connection at unix://%s.' % socket_path)
        return streamexpect.wrap(sock, window=Transport.WINDOW, close_stream=False)

    @staticmethod
    def get_instance():
        if Transport.__instance is None:
            Transport()
        return Transport.__instance

    @property
    def transport(self):
        if self.__proc is None:
            self.setupUMI(*self.DEFAULT_CONNECTION_CONFIG)  # default UMI configuration if not set up explicitly
        return self.__proc

    @staticmethod
    def _format(**kwargs):
        return json.dumps(kwargs, separators=(',', ':')).encode()

    def sync_call(self, name, full_response=False, **kwargs):
        cmd = self._format(serial=self.serial, cmd=name, **kwargs)
        logger.debug('   >> %s', cmd.decode())
        if self.method == 'pipe':
            self.transport.sendline(cmd)
            self.transport.expect('\r\n.*"ref":%s.*\r\n' % self.serial)
            rsp_text = self.transport.after
        else:
            self.transport.sendall(cmd + b'\r\n')
            match = self.transport.expect_regex((r'({.*"ref":%s.*})' % self.serial).encode())
            rsp_text = match.groups[0]

        try:
            rsp_text = rsp_text.decode()
        except Exception:
            pass
        finally:
            rsp_text = rsp_text.strip()

        self.serial += 1
        logger.debug('   << %s', rsp_text)
        rsp = json.loads(rsp_text)
        if 'error' in rsp:
            raise exceptions.UniversaException(rsp_text, rsp['error'])

        if not full_response:
            return rsp['result']
        else:
            return rsp

    @property
    def version(self):
        return self.sync_call('version')

    def test(self):
        return self.sync_call('version', full_response=True)

    def instantiate(self, object_type, *args):
        return self.sync_call('instantiate', args=[object_type] + list(args))

    def invoke(self, remote_object_id, method_name, *args):
        return self.sync_call('invoke', args=[remote_object_id, method_name] + list(args))

    def invoke_static(self, object_type, method_name, *args):
        return self.sync_call('invoke', args=[object_type, method_name] + list(args))

    def get(self, remote_object_id):
        return self.sync_call('get', args=[remote_object_id])

    def get_field(self, remote_object_id, field_name):
        return self.sync_call('get_field', args=[remote_object_id, field_name])

    def drop_objects(self, ids=None, drop_all=False):
        if not drop_all:
            to_delete = set()
            for _id in ids or []:
                to_delete.add(_id)
                if _id in self.OBJECTS:
                    self.OBJECTS.pop(_id, None)
            else:
                return self.sync_call('drop_objects', ids=list(to_delete))
        else:
            self.OBJECTS = weakref.WeakValueDictionary()
            return self.sync_call('drop_all')


transport = Transport()

setupUMI = Transport.setupUMI
