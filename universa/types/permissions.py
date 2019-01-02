# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from .base import Base


class ChangeNumberPermission(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.ChangeNumberPermission'


class ChangeOwnerPermission(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.ChangeOwnerPermission'


class ModifyDataPermission(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.ModifyDataPermission'


class RevokePermission(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.RevokePermission'


class SplitJoinPermission(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.permissions.SplitJoinPermission'
