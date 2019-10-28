
# Universa

[![Build status](https://travis-ci.org/vkovrigin/universa.svg?master)](https://travis-ci.org/vkovrigin/universa)
[![PyPI Downloads](https://img.shields.io/pypi/dm/universa.svg)](https://pypi.org/project/universa/)
[![Latest PyPI version](https://img.shields.io/pypi/v/universa.svg)](https://pypi.org/project/universa/)
[![License](https://img.shields.io/pypi/l/universa.svg)](https://pypi.org/project/universa/)

This is an under-construction official Python package from
[Universa](https://universablockchain.com)
to facilitate access to the Java library using Universa's UMI protocol.

## Installation

### Installation

```bash
pip install universa
```

## Usage

### Prerequisites

You need to have [UMI](https://kb.universablockchain.com/umi_protocol/98) installed somewhere on your system.
To run, UMI requires JVM v1.8.* (or newer) to be installed, too.

UMI can be used in one of three modes:

* `pipe` – the UMI instance is dynamically executed in a subprocess, and a pipe is used for communication.
* `tcp` – connect to an already running UMI instance via TCP socket.
* `unix` – connect to an already running UMI instance via Unix socket.

 By default it expects an `umi` binary to be installed an reachable via the shell `$PATH`, and will invoke it automatically in `pipe` mode.
 Use `universa.transport.setupUMI` method if you need to switch the connection method to some other.

### Example


```python
#!/usr/bin/env python3
from universa.transport import transport
from universa.types import PrivateKey, Contract, RevokePermission

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
```

## Docs and resources

For more information see:
- [Universa Knowledge Base](https://kb.universablockchain.com/)
- [Universa Java API](https://kb.universablockchain.com/general_java_api/5)
- [Universa UMI server](https://kb.universablockchain.com/umi_protocol/98)

## License

This package is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
