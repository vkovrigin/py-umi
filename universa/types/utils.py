# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from .base import transport, Base


class HashSet(Base):
    JAVA_CLASS = 'java.util.HashSet'

    def __init__(self, items=None, **kwargs):
        __items = set()
        for item in items or []:
            obj = None
            klass = self.get_class_by_type(item['__type'])
            if klass.__name__ == 'KeyAddress':
                obj = klass(uaddress=item['uaddress']['base64'])

            if obj is not None:
                __items.add(obj)

        super(HashSet, self).__init__(**kwargs)
        self.items = list(__items)

    @classmethod
    def get(cls, _id):
        instance = cls(id=_id, items=cls._get(_id), skip_update=True)
        transport.OBJECTS[_id] = instance
        return instance

    def update(self):
        self.items = self._get(self.id)

    def _instantiate_data(self):
        return
