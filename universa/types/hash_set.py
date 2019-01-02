# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from .base import transport, Base


class Set(Base):
    JAVA_CLASS = 'java.util.HashSet'
