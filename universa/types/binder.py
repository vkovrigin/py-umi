# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

try:
    from collections.abc import MutableMapping  # noqa
except ImportError:
    from collections import MutableMapping  # noqa
import json

from .base import Base


class Binder(Base, MutableMapping):
    JAVA_CLASS = 'net.sergeych.tools.Binder'

    LOCAL_ATTRS = ('id', '__initial')

    def __init__(self, *args, **kwargs):
        _id = kwargs.pop('id', None)
        self.__initial = dict(*args, **kwargs)
        super(Binder, self).__init__(id=_id)

    @property
    def __dict__(self):
        return self._get(self.id)

    def __getitem__(self, key):
        item = self._invoke('get', key)
        if isinstance(item, dict) and item.get('__type') == 'RemoteObject':
            remote_id = item.get('id')
            remote_class = item.get('className')
            if remote_id is not None and remote_class:
                return self.get_class_by_java(remote_class)(id=remote_id)
        return item

    def __setitem__(self, key, value):
        self._invoke('set', key, value)

    def __delitem__(self, key):
        self._invoke('remove', key)

    def __iter__(self):
        return iter(self.__dict__.items())

    def __len__(self):
        return len(self.__dict__)

    def setdefault(self, k, default=None):
        self._invoke('putIfAbsent', k, self.obj_umification(default))
        return self[k]

    def _instantiate_data(self):
        return self.kwargs_umification(self.__initial)
