# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class UniversaException(Exception):
    def __init__(self, message, error):
        super(UniversaException, self).__init__(message)
        self.error = error
