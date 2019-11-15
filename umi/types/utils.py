# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from .base import transport, Base


class HashSet(Base):
    JAVA_CLASS = 'java.util.HashSet'
    API_TYPE = 'Set'

    items = []

    def __init__(self, items=None, **kwargs):
        __items = []
        for item in items or []:
            if not isinstance(item, Base):
                klass = self.get_class_by_type(item['__type'])
                if klass.API_TYPE == 'KeyAddress':
                    item = klass(uaddress=item['uaddress']['base64'])

            if item is not None:
                __items.append(item)

        self.__items = __items
        super(HashSet, self).__init__(**kwargs)
        self.__position = 0

    def __iter__(self):
        for obj in self._invoke('toArray'):
            klass = self.get_class_by_java(obj['className'])
            yield klass.get(obj['id'])

    def __len__(self):
        return self._invoke('size')

    def __getitem__(self, item):
        obj = self._invoke('toArray')[item]
        klass = self.get_class_by_java(obj['className'])
        return klass.get(obj['id'])

    @classmethod
    def get(cls, _id):
        instance = cls(id=_id, items=cls._get(_id), skip_update=True)
        transport.OBJECTS[_id] = instance
        return instance

    def _instantiate_data(self):
        items = [item.remote if isinstance(item, Base) else item for item in self.__items]
        del self.__items
        return items
