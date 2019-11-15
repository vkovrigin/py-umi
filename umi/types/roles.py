# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .base import Base
from .crypto import KeyAddress


#
# Abstract
#
class Role(Base):
    class RequiredMode:
        ALL_OF = 'ALL_OF'  # In this mode, all references must be allowed for allows role
        ANY_OF = 'ANY_OF'  # In this mode, at least one of the references must be allowed for allows role
        MODES = [ALL_OF, ANY_OF]

    def __init__(self, name, **kwargs):
        self.name = name
        super(Role, self).__init__(name=name, **kwargs)

    def _instantiate_data(self):
        return self.name

    def anonymize(self):
        self._invoke('anonymize')

    def equals_ignore_name(self, obj):
        return self._equals('equalsIgnoreName', obj)

    def equals_ignore_name_and_refs(self, obj):
        return self._equals('equalsIgnoreNameAndRefs', obj)

    def get_comment(self):
        return self._invoke('getComment')

    def get_contract(self):
        from umi.types.contract import Contract
        rsp = self._invoke('getContract')
        return Contract.get(rsp['id']) if rsp is not None else None

    def get_name(self):
        return self._invoke('getName')

    def get_references(self, required_mode):
        if required_mode in [self.RequiredMode.MODES]:
            return self._invoke('getReferences', required_mode)
        return None

    def get_simple_address(self):
        """
        Get an address from the role, if it is just a single one. May be used to display
        a single bearer of a role in UIs. Returns null if a single address cannot be decided for the role
        (like, if there is no addresses/keys discoverable or if there is more than 1 address/key).
        If the role is bound to a public key rather than an address, returns its short address.

        :rtype: KeyAddress | None
        """
        key_address = self._invoke('getSimpleAddress')
        if key_address:
            return KeyAddress(id=key_address['id'])

    def hash_code(self):
        return self._invoke('hashCode')

    def is_valid(self):
        return self._invoke('isValid')

    def link_as(self, role_name):
        rsp = self._invoke('linkAs', role_name)
        return RoleLink.get(rsp['id'])

    def resolve(self):
        """
        Goes through the links to the first non-link role and returns the certain Role.
        May return None if RoleLink target is None (or is a recursive link).

        :rtype: Role | None
        """
        rsp = self._invoke('resolve')
        if rsp is not None:
            klass = self.get_class_by_java(rsp['className'])
            return klass.get(rsp['id'])
        else:
            return None

    def set_comment(self, comment):
        self._invoke('setComment', comment)

    def set_contract(self, contract):
        """
        :type contract: umi.types.contract.Contract
        :return:
        """
        self._invoke('setContract', contract.remote)

    def to_string(self):
        return self._invoke('toString')


#
# Real
#
class SimpleRole(Role):
    JAVA_CLASS = 'com.icodici.universa.contract.roles.SimpleRole'

    def __init__(self, name, records=None, **kwargs):
        """
        :type name: str
        :type records: list[KeyAddress] | None
        """
        self.__records = records
        super(SimpleRole, self).__init__(name=name, **kwargs)
        del self.__records

    def _instantiate_data(self):
        if self.__records is not None:
            return self.name, [r.remote for r in self.__records]
        return self.name

    def get_simple_anonymous_ids(self):
        return self._get_hashset('getSimpleAnonymousIds')

    def get_simple_key_addresses(self):
        return self._get_hashset('getSimpleKeyAddresses')

    def get_simple_key_records(self):
        return self._get_hashset('getSimpleKeyRecords')

    def get_simple_keys(self):
        return self._get_hashset('getSimpleKeys')


class ListRole(Role):
    JAVA_CLASS = 'com.icodici.universa.contract.roles.ListRole'

    class Mode:
        ALL = 'ALL'  # Role could be performed only if set of keys could play all sub-roles
        ANY = 'ANY'  # Role could be performed if set of keys could play any role of the list
        QUORUM = 'QUORUM'  # Role could be played if set of keys could play any quorrum set of roles, e.g.
        MODES = [ALL, ANY, QUORUM]


class RoleLink(Role):
    JAVA_CLASS = 'com.icodici.universa.contract.roles.RoleLink'

    def __init__(self, name, target_name, **kwargs):
        self.target_name = target_name
        super(RoleLink, self).__init__(name=name, target_name=target_name, **kwargs)

    def get_role(self):
        """
        Returns the target role it links to (may return one more RoleLink)
        and .resolve() goes through all links to find the first non-link role.

        :rtype: Role
        """
        rsp = self._invoke('getRole')
        if rsp is not None:
            klass = self.get_class_by_java(rsp['className'])
            return klass.get(rsp['id'])
        else:
            return None
