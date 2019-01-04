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
    BINARY = './umi/bin/umi'
    OBJECTS = {}

    __instance = None

    def __init__(self):
        if Transport.__instance is not None:
            logger.exception('Universa Transport is a singleton.')
            raise Exception('Universa Transport is a singleton.')

        Transport.__instance = self
        self.OBJECTS = weakref.WeakValueDictionary()
        self.__proc = None
        self.serial = 0

    def __del__(self):
        logger.info('Cleaning')
        self.drop_objects(drop_all=True)

    @staticmethod
    def get_instance():
        if Transport.__instance is None:
            Transport()
        return Transport.__instance

    @property
    def transport(self):
        if self.__proc is not None:
            return self.__proc
        self.__proc = pexpect.spawn(self.BINARY, timeout=None)
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
