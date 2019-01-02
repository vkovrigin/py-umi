# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import gc

from universa.transport import transport
from universa.types import PrivateKey


def test():
    gc.enable()

    assert len(transport.OBJECTS) == 0, 'transport objects are not blank'

    key = PrivateKey(size=2048)
    assert len(transport.OBJECTS) == 1, 'transport objects does not contains only one value'

    key2 = PrivateKey(size=2048)
    assert len(transport.OBJECTS) == 2, 'transport objects does not contains only two values'

    # Create a key overriding previous one variable.
    # GarbageCollector should delete old object and kill it from transport (and UMI remote object).
    key2 = PrivateKey(size=2048)
    assert len(transport.OBJECTS) == 2, 'transport objects does not contains only two values'

    # Create a key and don't save it to the variable. It should be deleted by UMI at once.
    PrivateKey(size=2048)
    assert len(transport.OBJECTS) == 2, 'transport objects does not contains only two values'

    # Delete a local key object. It should be removed from UMI too.
    del key2
    assert len(transport.OBJECTS) == 1, 'transport objects does not contains only one value'
