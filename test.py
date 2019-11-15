#!/usr/bin/env python3
from umi.transport import transport
from umi.types import PrivateKey, Contract, RevokePermission

if __name__ == '__main__':
    # The next line is not necessary if umi is reachable via the $PATH
    # transport.setupUMI('pipe', '/usr/local/bin/umi')

    # To connect to an already running UMI instance you may use one of this modes:
    # transport.setupUMI('tcp', host='127.0.0.1', port=12345)  # IPv6 is also ok
    # transport.setupUMI('unix', path='/path-to-the-socket')

    print(transport.version)

    private_key = PrivateKey(size=2048)
    contract = Contract()
    short_address = private_key.public_key.short_address
    owner_role = contract.set_owner_addresses(short_address)
    revoke_permission = RevokePermission(owner_role)
    contract.add_permission(revoke_permission)
