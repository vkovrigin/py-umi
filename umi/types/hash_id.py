# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from .base import Base


class HashId(Base):
    JAVA_CLASS = 'com.icodici.universa.HashId'

    def __init__(self, packed_data=None, **kwargs):
        # TODO: check this constructor
        # raise NotImplementedError()
        self.packed_data = packed_data
        super(HashId, self).__init__(**kwargs)

    def _instantiate_data(self):
        return self.packed_data

    @staticmethod
    def from_get(data):
        return {'packed_data': data['composite3']}

    def compare_to(self, obj):
        return self._equals('compareTo', obj)

    @classmethod
    def create_random(cls):
        return cls.get(cls._invoke_static('createRandom')['id'])

    def get_digest(self):
        return self._invoke('getDigest')

    @property
    def hash_code(self):
        return self._invoke('hashCode')

    def to_base64_string(self):
        return self._invoke('toBase64String')

    @classmethod
    def with_digest(cls, _hash=None, encoded=None):
        assert (_hash is None) ^ (encoded is None), 'either hash or encoded should be not None'
        rsp = cls._invoke_static('withDigest', _hash or encoded)
        return cls.get(rsp['id'])
