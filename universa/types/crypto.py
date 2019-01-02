# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .base import logger, Base


class AbstractKey(Base):
    def __init__(self, size=None, key=None, **kwargs):
        self.size = size
        self.key = key
        super(AbstractKey, self).__init__(size=size, key=key, **kwargs)
        self.pack()

    def _instantiate_data(self):
        if self.key is not None:
            return {'__type': 'binary', 'base64': self.key}
        elif self.size is not None:
            return self.size
        else:
            logger.exception('Can\'t find .instantiate_data() data for %s', self)
            return None

    def pack(self):
        rsp = self._invoke('pack')
        self.key = rsp['base64']
        return self.key


class KeyAddress(Base):
    JAVA_CLASS = 'com.icodici.crypto.KeyAddress'

    # __slots__ = ('id', 'address', 'uaddress')

    def __init__(self, address=None, uaddress=None, **kwargs):
        self.address = address
        self.uaddress = uaddress
        super(KeyAddress, self).__init__(address=address, uaddress=uaddress, **kwargs)

    def _instantiate_data(self):
        return self.address or ''

    @staticmethod
    def from_get(data):
        return {'uaddress': data['uaddress']['base64']}

    def is_matching_key_address(self, key_address):
        if key_address is None or self.JAVA_CLASS != key_address.JAVA_CLASS or key_address.id is None:
            return False

        rsp = self._invoke('isMatchingKeyAddress', key_address.remote)
        return rsp

    def get_packed(self):
        if self.uaddress:
            return self.uaddress
        self.uaddress = self._invoke('getPacked')['base64']
        return self.uaddress

    @property
    def is_long(self):
        return self._invoke('isLong')

    def to_string(self):
        self.address = self._invoke('toString')
        return self.address


class PrivateKey(AbstractKey):
    JAVA_CLASS = 'com.icodici.crypto.PrivateKey'

    # __slots__ = ('id', 'size', 'packed', 'key')

    def __init__(self, size=None, key=None, **kwargs):
        super(PrivateKey, self).__init__(size=size, key=key, **kwargs)
        self._public_key = None

    @staticmethod
    def from_get(data):
        return {'packed': data['packed']}

    def get_public_key(self):
        rsp = self._invoke('getPublicKey')
        self._public_key = PublicKey.get(rsp['id'])
        return self._public_key

    @property
    def public_key(self):
        if self._public_key is not None:
            return self._public_key

        return self.get_public_key()


class PublicKey(AbstractKey):
    JAVA_CLASS = 'com.icodici.crypto.PublicKey'

    # __slots__ = ('id', 'size', 'key')

    def __init__(self, **kwargs):
        self._short_address, self._long_address = None, None
        super(PublicKey, self).__init__(**kwargs)

    @staticmethod
    def from_get(data):
        return {'key': data['packed']['base64']}

    def _get_address(self, short=True):
        rsp = self._invoke('getShortAddress' if short else 'getLongAddress')
        instance = KeyAddress.get(rsp['id'])
        instance.to_string()
        setattr(self, '_short_address' if short else '_long_address', instance)
        return instance

    @property
    def short_address(self):
        return self._short_address if self._short_address is not None else self.get_short_address()

    def get_short_address(self):
        return self._get_address(short=True)

    @property
    def long_address(self):
        return self._long_address if self._long_address is not None else self.get_long_address()

    def get_long_address(self):
        return self._get_address(short=False)
