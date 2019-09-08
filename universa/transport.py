# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import weakref

import pexpect

try:
    from farcall import Farcall
except ImportError:
    Farcall = None

from universa import logging
from universa import exceptions

logger = logging.getLogger()


class Transport(object):
    OBJECTS = {}

    __instance = None
    __proc = None

    def __init__(self):
        if Transport.__instance is not None:
            logger.exception('Universa Transport is a singleton.')
            raise Exception('Universa Transport is a singleton.')

        Transport.__instance = self
        self.OBJECTS = weakref.WeakValueDictionary()
        self.serial = 0

    def __del__(self):
        logger.info('Cleaning')
        self.drop_objects(drop_all=True)

    @classmethod
    def setupUMI(cls, method, path=None, host=None, port=None):
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
        assert method in ('pipe', 'tcp', 'unix'), method
        if method == 'pipe':
            if not path:
                raise ValueError('In "pipe" mode, you should provide non-empty "path" for UMI binary!')
            builder = lambda: cls.__make_pexpect_pipe_transport(path)
        elif method == 'tcp':
            if not host or not port:
                raise ValueError('In "tcp" mode, you should provide non-empty "host" and "port" for UMI TCP socket!')
            builder = lambda: cls.__make_pexpect_tcp_transport(host, port)
        elif method == 'unix':
            if not path:
                raise ValueError('In "unix" mode, you should provide non-empty "path" for UMI Unix socket!')
            builder = lambda: cls.__make_pexpect_unix_transport(path)
        else:
            raise ValueError('Unsupported method {}'.format())

        # We have a `builder` defined here.
        # Do we have a running transport already?
        if cls.__proc is not None:
            cls.__instance.drop_objects(drop_all=True)

        cls.__proc = builder()

    @staticmethod
    def __make_pexpect_pipe_transport(binary_path):
        try:
            return pexpect.spawn(binary_path, timeout=None)
        except pexpect.exceptions.ExceptionPexpect as e:
            if e.value.startswith('The command was not found or was not executable:'):
                raise ValueError('UMI executable you have chosen is not available at the requested path (or in $PATH).')
            else:
                raise

    @staticmethod
    def __make_pexpect_tcp_transport(host, port):
        raise NotImplementedError()

    @staticmethod
    def __make_pexpect_unix_transport(path):
        raise NotImplementedError()

    @staticmethod
    def get_instance():
        if Transport.__instance is None:
            Transport()
        return Transport.__instance

    @property
    def transport(self):
        if self.__proc is None:
            setupUMI('pipe', 'umi')  # default UMI configuration if not set up explicitly
        return self.__proc

    def _format(self, **kwargs):
        return json.dumps(kwargs, separators=(',', ':'))

    def sync_call(self, name, **kwargs):
        cmd = self._format(serial=self.serial, cmd=name, **kwargs)
        logger.info('   >> executing cmd: %s', cmd)
        self.transport.sendline(cmd)
        self.transport.expect('\r\n.*"ref":%s.*\r\n' % self.serial)
        self.serial += 1
        rsp_text = self.transport.after.decode().strip()
        rsp = json.loads(rsp_text)
        logger.info('   << response: %s', rsp)
        if 'error' in rsp:
            logger.exception('Universa exception caught: %s', rsp_text)
            raise exceptions.UniversaException(rsp_text, rsp['error'])
        return rsp['result']

    def version(self):
        return self.sync_call('version')

    def instantiate(self, object_type, *args):
        return self.sync_call('instantiate', args=[object_type] + list(args))

    def invoke(self, remote_object_id, method_name, *args):
        return self.sync_call('invoke', args=[remote_object_id, method_name] + list(args))

    def invoke_static(self, object_type, method_name, *args):
        return self.sync_call('invoke', args=[object_type, method_name] + list(args))

    def get(self, remote_object_id):
        return self.sync_call('get', args=[remote_object_id])

    def drop_objects(self, ids=None, drop_all=False):
        ids = ids if ids is not None else []
        to_delete = set()
        if not drop_all:
            for _id in ids:
                if _id in self.OBJECTS:
                    to_delete.add(_id)
                    self.OBJECTS.pop(_id, None)
        else:
            to_delete = list(self.OBJECTS.keys())
            self.OBJECTS = weakref.WeakValueDictionary()

        if to_delete:
            return self.sync_call('drop_objects', ids=list(to_delete))


transport = Transport()

setupUMI = Transport.setupUMI
