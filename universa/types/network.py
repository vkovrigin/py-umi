# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from .base import Base


class Client(Base):
    JAVA_CLASS = 'com.icodici.universa.node2.network.Client'
