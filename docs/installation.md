# Install package
 
```bash
pip install py-umi
```


# Prerequisites

You need to have [UMI](https://kb.universablockchain.com/umi_protocol/98) installed somewhere on your system.
To run, UMI requires JVM v1.8.* (or newer) to be installed, too.

UMI can be used in one of three modes:

* `pipe` – the UMI instance is dynamically executed in a subprocess, and a pipe is used for communication.
* `tcp` – connect to an already running UMI instance via TCP socket.
* `unix` – connect to an already running UMI instance via Unix socket.

 By default it expects an `umi` binary to be installed an reachable via the shell `$PATH`, and will invoke it automatically in `pipe` mode.
 Use `umi.transport.setupUMI` method if you need to switch the connection method to some other.

