# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .base import DEFAULT_CLASS, TYPES_CLASS_MAP, JAVA_CLASS_MAP, Base
from .binder import Binder
from .contract import ContractsService, Reference, Contract, Parcel, ExtendedSignature
from .crypto import KeyAddress, PrivateKey, PublicKey
from .hash_id import HashId
from .network import Client
from .permissions import ChangeNumberPermission, ChangeOwnerPermission, ModifyDataPermission, RevokePermission, SplitJoinPermission
from .roles import SimpleRole, ListRole, RoleLink
from .utils import HashSet


def __all_subclasses(cls):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in __all_subclasses(c)])


def __load_class_map():
    for klass in __all_subclasses(Base):
        klass._set_api_type()
        java_class, _type = getattr(klass, 'JAVA_CLASS'), getattr(klass, 'API_TYPE')
        if java_class and _type:
            JAVA_CLASS_MAP[java_class] = klass
            TYPES_CLASS_MAP[_type] = klass


__load_class_map()


# def get_object(_id, data):
#     klass_name = data['__type']
#     klass = CLASS_MAP.get(klass_name, DEFAULT_CLASS)
#     obj = klass(_id, **data)
#     return obj
