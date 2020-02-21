[![Test](https://github.com/tmbdev/objio/workflows/Test/badge.svg)](http://github.com/tmbdev/objio/actions)
[![TestPip](https://github.com/tmbdev/objio/workflows/TestPip/badge.svg)](http://github.com/tmbdev/objio/actions)
[![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/tmbdev/objio/?ref=repository-badge)

# The Object IO Library and Command

Object stores (S3, Google, Azure, Minio, Swift, etc.) all have their own
command line interfaces with their own conventions for accessing objects.
This library and command provides a simple, uniform interface to object
store facilities, both from the command line and from within Python.


# Installation

```Bash
    $ pip install objio
```

For the Github version:

```Bash
    $ pip install git+https://github.com/tmbdev/objio.git
```

# Documentation

[ReadTheDocs](http://objio.readthedocs.io)

# Command Line Usage

```Bash
    $ obj cat az://container/blobname
    $ obj cat gs://bucket/blobname
    $ obj cat s3://bucket/blobname
    $ obj cat file:/path
    $ cat file | obj put gs://bucket/blobname
```

# Python Usage

```Python
    import objio

    with objio.gopen("gs://bucket/blob", "rb") as stream:
        contents = stream.read()
```

# New Protocols

You can define new schemes by creating a `./ojbio.yaml` or `~/.objio.yaml`
file. For example:

```YAML
    schemes:
        random:
            read:
                cmd: ["cat", "/dev/random"]
```

# Documentation

You can find documentation at ![Read The Docs](http://objio.readthedocs.io)

# Future Extensions

The intention is to keep this library simple and always allow command line
programs to be configured for I/O as needed by end users.

Additional functionality:

- better error handling of non-zero return codes
- `obj dir az://container --format csv`
- `obj del gs://container/blob`
- possibly port to Go 

Note that for Python, running I/O in a separate process is _preferable_ to using
Python-native libraries, since the latter do not run concurrently. For a Go
language implementation, protocol implementations using built in native client
libraries are potentially useful.
