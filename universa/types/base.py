# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from universa import logging
from universa.transport import transport


logger = logging.getLogger()


class Base(object):
    JAVA_CLASS = ''
    API_TYPE = ''

    __slots__ = ('id', '__weakref__')

    def __init__(self, skip_update=False, **kwargs):
        self.id = kwargs.get('id')

        if self.id is None:
            for k, v in self.from_instantiate(self._instantiate()).items():
                setattr(self, k, v)
            transport.OBJECTS[self.id] = self

        if self.id is not None and not skip_update:
            self.update()

    def __str__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.id)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.id)

    def __del__(self):
        logger.info('Deleting local %s', self)
        if self.id and transport:
            transport.drop_objects([self.id])

    @classmethod
    def _set_api_type(cls):
        cls.API_TYPE = cls.JAVA_CLASS.split('.')[-1].replace('$', '.')

    @staticmethod
    def get_class_by_java(java_class_name):
        return JAVA_CLASS_MAP.get(java_class_name, DEFAULT_CLASS)

    @staticmethod
    def get_class_by_type(api_type):
        return TYPES_CLASS_MAP.get(api_type, DEFAULT_CLASS)

    def _instantiate(self):
        args = [self.__class__.__name__]
        data = self._instantiate_data()
        if data is not None:
            args.append(data)
        return transport.instantiate(*args)

    def _invoke(self, method_name, *args):
        return transport.invoke(self.id, method_name, *args)

    def _invoke_static(self, method_name, *args):
        return transport.invoke_static(self.API_TYPE, method_name, *args)

    @classmethod
    def _get(cls, _id):
        return cls.from_get(transport.get(_id))

    @classmethod
    def get(cls, _id):
        data = cls._get(_id)
        data['id'] = _id
        instance = cls(skip_update=True, **data)
        transport.OBJECTS[_id] = instance
        return instance

    def update(self):
        for k, v in self._get(self.id).items():
            setattr(self, k, v)

    @property
    def remote(self):
        if isinstance(self, Base) and self.id is not None:
            return {'__type': 'RemoteObject', 'className': self.JAVA_CLASS, 'id': self.id}

    def equals(self, obj):
        if id(self) == id(obj):
            return True

        if self.JAVA_CLASS != obj.JAVA_CLASS:
            return False

        return self._invoke('equals', obj.remote)

    def _instantiate_data(self):
        raise NotImplementedError()

    @staticmethod
    def from_instantiate(data):
        return {'id': data['id']}

    @staticmethod
    def from_get(data):
        return data


DEFAULT_CLASS = Base
TYPES_CLASS_MAP = {}
JAVA_CLASS_MAP = {}
