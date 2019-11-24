# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

from pexpect.fdpexpect import fdspawn as pexpect_fdspawn


class fdspawn(pexpect_fdspawn):
    def __init__(self, fd_read, fd_write, *args, **kwargs):
        super(fdspawn, self).__init__(fd_read, *args, **kwargs)

        if type(fd_write) != type(0) and hasattr(fd_write, 'fileno'):
            fd_write = fd_write.fileno()

        self.fd_write = fd_write

    def send(self, s):
        s = self._coerce_send_string(s)
        self._log(s, 'send')

        b = self._encoder.encode(s, final=False)
        return os.write(self.fd_write, b)

    def close(self):
        try:
            os.close(self.fd_write)
        except OSError:
            pass
        else:
            self.fd_write = -1

        return super(fdspawn, self).close()
