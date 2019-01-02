# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from .base import Base


class SimpleRole(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.roles.SimpleRole'


class ListRole(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.roles.ListRole'


class RoleRequiredMode(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.roles.Role$RequiredMode'


class ListRoleMode(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.roles.ListRole$Mode'


class RoleLink(Base):
    JAVA_CLASS = 'com.icodici.universa.contract.roles.RoleLink'
