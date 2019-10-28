# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import warnings
from base64 import b64encode

from .base import Base
from .binder import Binder
from .crypto import KeyAddress, PrivateKey, PublicKey
from .hash_id import HashId
from .roles import Role
from .permissions import Permission
from .utils import HashSet
from universa.exceptions import UniversaException
from universa.utils import ut, dt


class Contract(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.Contract'
    ROLES = ['creator', 'issuer', 'owner']

    def __init__(self, binary=None, **kwargs):
        self._binary = binary
        super(Contract, self).__init__(**kwargs)

    @classmethod
    def from_packed(cls, from_packed):
        raise NotImplementedError()

    def _instantiate_data(self):
        if self._binary is not None:
            return {'__type': 'binary', 'base64': self._binary}

    def __set_role(self, role_name, *addresses):
        """
        Set provided addresses to the role.
        It's recommended to use KeyAddress instances, not PublicKey.
        PrivateKey is not allowed!

        :type addresses: list[KeyAddress | str]
        :returns: Role
        """
        if role_name not in self.ROLES:
            return

        __addresses = []
        for address in addresses:
            __addr = None
            if isinstance(address, KeyAddress):
                __addr = address
            elif isinstance(address, PublicKey):
                warnings.warn('It\'s recommended to use KeyAddress instances, not PublicKey.',
                              PendingDeprecationWarning)
                __addr = address.short_address
            elif isinstance(address, PrivateKey):
                warnings.warn('PrivateKey instance is not allowed! Use KeyAddress instead.',
                              SyntaxWarning)
                __addr = address.public_key.short_address
            elif isinstance(address, str):
                try:
                    __addr = KeyAddress(address=address)
                except UniversaException as e:
                    if 'Not a Base58 input' in e.error.get('text', ''):
                        try:
                            __addr = KeyAddress(uaddress=address)
                        except UniversaException:
                            pass

            if __addr is not None:
                __addresses.append(__addr)

        cmd = 'set{}Keys'.format(role_name.capitalize())
        rsp = self._invoke(cmd, *__addresses)
        klass = self.get_class_by_java(rsp['className'])
        return klass.get(rsp['id'])

    def set_creator_keys(self, *keys):
        """Set 'creator' role to given keys."""
        warnings.warn('Contract.set_creator_keys(*keys) will be deprecated. '
                      'Use contract.set_creator_addresses(*addresses) instead.',
                      PendingDeprecationWarning)
        return self.set_creator_addresses(*keys)

    def set_issuer_keys(self, *keys):
        """Set 'issuer' role to given keys."""
        warnings.warn('Contract.set_issuer_keys(*keys) will be deprecated. '
                      'Use contract.set_issuer_addresses(*addresses) instead.',
                      PendingDeprecationWarning)
        return self.set_issuer_addresses(*keys)

    def set_owner_keys(self, *keys):
        """Set 'owner' role to given keys."""
        warnings.warn('Contract.set_owner_keys(*keys) will be deprecated. '
                      'Use contract.set_owner_addresses(*addresses) instead.',
                      PendingDeprecationWarning)
        return self.set_owner_addresses(*keys)

    def set_creator_addresses(self, *addresses):
        """Set 'creator' role to given addresses."""
        return self.__set_role('creator', *addresses)

    def set_issuer_addresses(self, *addresses):
        """Set 'issuer' role to given addresses."""
        return self.__set_role('issuer', *addresses)

    def set_owner_addresses(self, *addresses):
        """Set 'owner' role to given addresses."""
        return self.__set_role('owner', *addresses)

    def get_role(self, role_name):
        if role_name in self.ROLES:
            rsp = self._invoke('get{}'.format(role_name.capitalize()))
        else:
            rsp = self._invoke('getRole', role_name)

        if rsp is not None:
            klass = self.get_class_by_java(rsp['className'])
            return klass.get(rsp['id'])
        else:
            return None

    def get_creator(self):
        return self.get_role('creator')

    def get_issuer(self):
        return self.get_role('issuer')

    def get_owner(self):
        return self.get_role('owner')

    def create_role(self, name, role):
        """
        :type name: str
        :type role: Role
        :return: Role
        """
        rsp = self._invoke('createRole', name, role.remote)
        klass = self.get_class_by_java(rsp['className'])
        return klass.get(rsp['id'])

    def get_created_at(self):
        """
        :return: unix time
        :rtype: datetime | None
        """
        rsp = self._invoke('getCreatedAt')
        return dt(rsp['seconds'])
    created_at = property(get_created_at)

    def get_expires_at(self):
        """
        :return: unix time
        :rtype: datetime | None
        """
        rsp = self._invoke('getExpiresAt')
        return dt(rsp['seconds']) if rsp is not None else None

    def set_expires_at(self, expires_at):
        """
        :param expires_at: unix time
        :type expires_at: datetime
        """
        self._invoke('setExpiresAt', {'seconds': ut(expires_at), '__type': 'unixtime'} 
                                         if expires_at is not None 
                                         else None)
    expires_at = property(get_expires_at, set_expires_at)

    def add_permission(self, permission):
        """
        :type permission: Permission
        """
        self._invoke('addPermission', permission.remote)

    def get_permissions(self):
        raise NotImplementedError()
        rsp = self._invoke('getPermissions')

    def is_permitted(self, permission_name, *keys):
        """
        Checks if permission of given type that is allowed for given keys exists.

        :type permission_name: str
        :type keys: PublicKey
        :rtype: bool
        """
        return self._invoke('isPermitted', permission_name, [key.remote for key in keys])

    def check_applicable_permission_quantized(self, permission):
        """
        Quantize given permission (add cost for that permission).

        :type permission: Permission
        """
        self._invoke('checkApplicablePermissionQuantized', permission.remote)

    def seal(self):
        return self._invoke('seal')['base64']

    def check(self):
        return self._invoke('check')

    def get_errors(self):
        return self._invoke('getErrors')

    def get_packed_transaction(self):
        return self._invoke('getPackedTransaction')

    def get_origin(self):
        return HashId(id=self._invoke('getOrigin')['id'])

    def get_id(self):
        return HashId(id=self._invoke('getId')['id'])

    def get_state_data(self):
        rsp = self._invoke('getStateData')
        return Binder.get(rsp['id'])

    def set_state(self, name, value):
        remote = self._invoke_static_with_type('Binder', 'of', value)
        self._invoke('set', name,  remote)

    def get_processed_cost(self):
        return self._invoke('getProcessedCost')

    def get_processed_cost_u(self):
        return self._invoke('getProcessedCostU')

    def get_transaction_pack(self):
        rsp = self._invoke('getTransactionPack')
        return TransactionPack(id=rsp['id'])

    def get_new_items(self):
        return HashSet(id=self._invoke('getNewItems')['id'])

    def get_revoking_items(self):
        return HashSet(id=self._invoke('getRevokingItems')['id'])

    @classmethod
    def from_sealed_binary(cls, sealed_binary):
        """

        :type sealed_binary: bytes
        :rtype: Contract
        """
        rsp = cls._invoke_static('fromSealedBinary', {'__type': 'binary', 'base64': b64encode(sealed_binary).decode()})
        return Contract(id=rsp['id'])


class TransactionPack(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.TransactionPack'

    def _instantiate_data(self):
        pass

    @classmethod
    def unpack(cls, pack_or_contract_bytes, allow_non_transactions=None):
        """
        :type pack_or_contract_bytes: bytes
        :type allow_non_transactions: bool | None
        """
        rsp = cls._invoke_static('unpack', {'__type': 'binary', 'base64': b64encode(pack_or_contract_bytes).decode()})
        return TransactionPack(id=rsp['id'])

    def set_contract(self, contract):
        """
        :type contract: Contract
        """
        self._invoke('setContract', contract)

    def get_contract(self):
        """
        :rtype: Contract
        """
        return Contract(id=self._invoke('getContract')['id'])


class ContractsService(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.ContractsService'

    @classmethod
    def create_split_join(cls, contracts_to_join, amounts_to_split, addresses_to_split, owner_keys,
                          field_name='amount'):
        """

        :type contracts_to_join: list[Contract]
        :type amounts_to_split: list[str]
        :type addresses_to_split: list[KeyAddress]
        :type owner_keys: HashSet[PrivateKey]
        :type field_name: str
        :rtype: list[Contract]
        """
        return [Contract(id=row['id'])
                    for row in cls._invoke_static('createSplitJoin', contracts_to_join, amounts_to_split,
                                                  addresses_to_split, owner_keys, field_name)]


class Reference(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.Reference'


class Parcel(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.Parcel'

    def __init__(self, **kwargs):
        super(Parcel, self).__init__(**kwargs)

    def _instantiate_data(self):
        return

    @classmethod
    def of(cls, payload, u_contract, u_keys):
        """
        :type payload: Contract
        :type u_contract: Contract
        :type u_keys: list[PrivateKey]
        :rtype: Parcel
        """
        rsp = cls._invoke_static('of', payload, u_contract, u_keys)
        return Parcel(id=rsp['id'])

    def pack(self):
        return self._invoke('pack')

    def get_payload(self):
        return TransactionPack(id=self._invoke('getPayload')['id'])

    def get_payment(self):
        return TransactionPack(id=self._invoke('getPayment')['id'])


class ExtendedSignature(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.ExtendedSignature'

