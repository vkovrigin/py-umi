# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from universa import logging
from universa.exceptions import UniversaException
from universa.transport import transport


logger = logging.getLogger()


class Base(object):
    JAVA_CLASS = ''
    API_TYPE = ''

    LOCAL_ATTRS = ('id',)

    __slots__ = ('id', '__weakref__')

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')

        if self.id is None:
            for k, v in self.from_instantiate(self._instantiate()).items():
                setattr(self, k, v)
            transport.OBJECTS[self.id] = self

    def __str__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.id)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.id)

    def __del__(self):
        logger.debug('Deleting local %s', self)
        if self.id and transport:
            transport.drop_objects([self.id])

    def __getattr__(self, item):
        if item in self.LOCAL_ATTRS:
            return self.__getattribute__(item)

        if self.id is not None:
            try:
                data = self._get_field(self.id, item)
            except UniversaException:
                raise AttributeError('{class_name!r} object has no attribute {attr!r}'
                                         .format(class_name=self.__class__.__name__, attr=item))
            return data

    # def __setattr__(self, key, value):
    #     if key in self.LOCAL_ATTRS:
    #         super(Base, self).__setattr__(key, value)
    #
    #     if self.id is not None:
    #         self._invoke('set', key, value)
    #     else:
    #         raise AttributeError

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self.equals(other)

    @classmethod
    def _set_api_type(cls):
        cls.API_TYPE = cls.API_TYPE or cls.JAVA_CLASS.split('.')[-1].replace('$', '.')

    @staticmethod
    def get_class_by_java(java_class_name):
        return JAVA_CLASS_MAP.get(java_class_name, DEFAULT_CLASS)

    @staticmethod
    def get_class_by_type(api_type):
        return TYPES_CLASS_MAP.get(api_type, DEFAULT_CLASS)

    @classmethod
    def obj_umification(cls, obj):
        if isinstance(obj, Base):
            obj = obj.remote
        elif isinstance(obj, dict):
            obj = cls.kwargs_umification(obj)
        elif isinstance(obj, (tuple, list, set)):
            obj = cls.args_umification(obj)
        return obj

    @classmethod
    def args_umification(cls, args):
        umi_args = []
        for obj in args:
            umi_args.append(cls.obj_umification(obj))
        return umi_args

    @classmethod
    def kwargs_umification(cls, dct):
        umi_dct = {}
        for key, value in dct.items():
            umi_dct[cls.obj_umification(key)] = cls.obj_umification(value)
        return umi_dct

    def _instantiate(self):
        args = [self.__class__.API_TYPE]
        data = self._instantiate_data()
        if data is not None:
            if isinstance(data, tuple):
                args.extend(data)
            else:
                args.append(data)
        return transport.instantiate(*args)

    def _invoke(self, method_name, *args):
        return transport.invoke(self.id, method_name, *self.args_umification(args))

    @classmethod
    def _invoke_static_with_type(cls, api_type, method_name, *args):
        return transport.invoke_static(api_type, method_name, *cls.args_umification(args))

    @classmethod
    def _invoke_static(cls, method_name, *args):
        return cls._invoke_static_with_type(cls.API_TYPE, method_name, *cls.args_umification(args))

    @classmethod
    def _get(cls, _id):
        return cls.from_get(transport.get(_id))

    @classmethod
    def _get_field(cls, _id, field_name):
        return cls.from_get(transport.get_field(_id, field_name))

    @classmethod
    def get(cls, _id):
        data = cls._get(_id)
        instance = cls(id=_id, skip_update=True, **data)
        # TODO: probably we don't want to save this object to the transport cause it may not be saved to a variable
        transport.OBJECTS[_id] = instance
        return instance

    def update(self):
        for k, v in self._get(self.id).items():
            setattr(self, k, v)

    @property
    def remote(self):
        if isinstance(self, Base) and self.id is not None:
            return {'__type': 'RemoteObject', 'className': self.JAVA_CLASS, 'id': self.id}

    def _get_hashset(self, cmd):
        rsp = self._invoke(cmd)
        if rsp is not None:
            klass = self.get_class_by_java(rsp['className'])
            return klass.get(rsp['id'])
        else:
            return None

    def _equals(self, equals_method_name, obj):
        if id(self) == id(obj):
            return True

        if self.JAVA_CLASS != obj.JAVA_CLASS:
            return False

        return self._invoke(equals_method_name, obj.remote)

    def equals(self, obj):
        return self._equals('equals', obj)

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
