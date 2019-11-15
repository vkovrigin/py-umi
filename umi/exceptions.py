# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class UMIException(Exception):
    def __init__(self, message, error):
        super(UMIException, self).__init__(message)
        self.error = error
