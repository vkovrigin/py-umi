# py-umi

[![Build status](https://travis-ci.org/vkovrigin/py-umi.svg?master)](https://travis-ci.org/vkovrigin/py-umi)
[![PyPI Downloads](https://img.shields.io/pypi/dm/py-umi.svg)](https://pypi.org/project/py-umi/)
[![Latest PyPI version](https://img.shields.io/pypi/v/py-umi.svg)](https://pypi.org/project/py-umi/)
[![License](https://img.shields.io/pypi/l/py-umi.svg)](https://pypi.org/project/py-umi/)

This is an under-construction official Python package from
[Universa](https://universablockchain.com)
to facilitate access to the Java library using Universa's UMI protocol.

## Example

```python
#!/usr/bin/env python3
from umi.types import PrivateKey, Contract, RevokePermission

if __name__ == '__main__':
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
