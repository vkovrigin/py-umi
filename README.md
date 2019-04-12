
# Universa

[![Build status](https://travis-ci.org/vkovrigin/universa.svg?master)](https://travis-ci.org/vkovrigin/universa)

This is an under-construction official python package from
[Universa](https://universablockchain.com)
to facilitate access to the Java library using Universa's UMI protocol.

## Installation

### Prerequisites

JVM v1.8.* must be installed.

### Installation

```bash
pip install universa
```

## Usage

```python
#!/usr/bin/env python3
from universa.transport import transport
from universa.types import PrivateKey, Contract, RevokePermission

if __name__ == '__main__':
    print(transport.version())

    private_key = PrivateKey(size=2048)
    contract = Contract()
    short_address = private_key.public_key.short_address
    owner_role = contract.set_owner_addresses(short_address)
    revoke_permission = RevokePermission(owner_role)
    contract.add_permission(revoke_permission)
```

## Docs and resources

For more information see:
- [Universa Knowledge Base](https://kb.universablockchain.com/)
- [Universa Java API](https://kb.universablockchain.com/general_java_api/5)
- [Universa UMI server](https://kb.universablockchain.com/umi_protocol/98)

## License

This package is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
