# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from .base import Base


class Permission(Base):
    def __init__(self, name=None, role=None, params=None, **kwargs):
        """

        :type name: str | None
        :type role: universa.types.roles.Role | None
        :type params: dict | None
        """
        self._name = name
        self._role = role
        self._params = params
        super(Permission, self).__init__(**kwargs)

    def _instantiate_data(self):
        if all(i is not None for i in [self._name, self._role, self._params]):
            return self._name, self._role.remote, self._params
        elif self._name is not None and self._role is not None:
            return self._name, self._role.remote
        else:
            return None

    def compare_to(self, obj):
        return self._equals('compareTo', obj)

    def get_id(self):
        """
        :rtype: int | None
        """
        return self._invoke('getId')

    def set_id(self, _id):
        """
        :type _id: int
        """
        return self._invoke('setId', _id)

    def get_name(self):
        """
        :rtype: str
        """
        return self._invoke('getName')

    def get_params(self):
        """
        :rtype:
        """
        raise NotImplementedError()
        return self._invoke('getParams')

    def get_role(self):
        """
        :rtype: universa.types.roles.Role | None
        """
        rsp = self._invoke('getRole')
        if rsp is not None:
            klass = self.get_class_by_java(rsp['className'])
            return klass.get(rsp['id'])
        else:
            return None

    def is_allowed_for_keys(self, *keys):
        """
        :type keys: universa.types.crypto.PublicKey
        :rtype: bool
        """
        return self._invoke('isAllowedForKeys', *[key.remote for key in keys])

    # TODO:
    # abstract void	checkChanges(Contract contract, Contract changed, java.util.Map<java.lang.String,net.sergeych.diff.Delta> stateChanges, java.util.Set<Contract> revokingItems, java.util.Collection<com.icodici.crypto.PublicKey> keys)
    # void	deserialize(net.sergeych.tools.Binder data, net.sergeych.biserializer.BiDeserializer deserializer)
    # static Permission	forName(java.lang.String name, Role role, net.sergeych.tools.Binder params)
    # net.sergeych.tools.Binder	getParams()
    # net.sergeych.tools.Binder	serialize(net.sergeych.biserializer.BiSerializer serializer)



class ChangeNumberPermission(Permission):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.ChangeNumberPermission'


class ChangeOwnerPermission(Permission):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.ChangeOwnerPermission'


class ModifyDataPermission(Permission):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.ModifyDataPermission'


class RevokePermission(Permission):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.RevokePermission'

    def __init__(self, role, **kwargs):
        """
        :type role: universa.types.roles.Role
        """
        super(RevokePermission, self).__init__(role=role, **kwargs)

    def _instantiate_data(self):
        return self._role.remote


class SplitJoinPermission(Permission):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.SplitJoinPermission'
