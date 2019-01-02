# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from datetime import datetime, timedelta

from .base import Base
from .crypto import KeyAddress, PrivateKey, PublicKey
from .roles import SimpleRole


class ContractsService(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.ContractsService'


class Reference(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.Reference'


class Contract(Base):
    # __slots__ = ('id', 'issuer_key', 'expires_at')

    JAVA_CLASS = 'com.icodici.universa.contract.Contract'
    ROLES = ['creator', 'issuer', 'owner']

    @staticmethod
    def get_role_name_id(role_name):
        return '_{}_id'.format(role_name)

    @classmethod
    def from_packed(cls, from_packed):
        raise NotImplementedError()

    def _instantiate_data(self):
        return

    def __set_role(self, role_name, *keys):
        if role_name not in self.ROLES:
            return

        cmd = 'set{}Keys'.format(role_name.capitalize())
        rsp = self._invoke(cmd, *[key.remote for key in keys])
        setattr(self, self.get_role_name_id(role_name), rsp['id'])

    def set_creator_keys(self, *keys):
        self.__set_role('creator', *keys)

    def set_issuer_keys(self, *keys):
        """
        Set "issuer" role to given keys.
        It's recommended to use KeyAddress instances, not PublicKey or PrivateKey.

        :param keys: keys to set "issuer" role to
        :type keys: list[KeyAddress | PrivateKey | PublicKey]
        :return: issuer role
        :returns: SimpleRole
        """
        self.__set_role('issuer', *keys)

    def set_owner_keys(self, *keys):
        self.__set_role('owner', *keys)

    def __get_role(self, role_name, data=None):
        if role_name not in self.ROLES:
            return

        rsp = data or self._get(self.id)

        if role_name == 'owner':
            role = rsp['definition'][role_name]
        elif role_name == 'creator':
            role = rsp['state']['created_by']
        elif role_name == 'issuer':
            role = rsp['state'][role_name]
        else:
            raise NotImplementedError()

        if role:
            klass = self.get_class_by_type(role['__type'])
            role_id = getattr(self, self.get_role_name_id(role_name), None)
            if role_id is not None:
                # We already have ID for remote object.
                return klass.get(role_id)
            else:
                # We don't have ID for remote object (i.e. when contract was uploaded)
                pass


    def get_creator(self):
        return self.__get_role('creator')

    def get_issuer(self):
        return self.__get_role('issuer')

    def get_owner(self):
        return self.__get_role('owner')


class Parcel(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.Parcel'


class ExtendedSignature(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.ExtendedSignature'

