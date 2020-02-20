![Test](https://github.com/tmbdev/objio/workflows/Test/badge.svg)

# The Object IO Library and Command

Object stores (S3, Google, Azure, Minio, Swift, etc.) all have their own
command line interfaces with their own conventions for accessing objects.
This library and command provides a simple, uniform interface to object
store facilities, both from the command line and from within Python.

# Command Line Usage

```Bash
    $ obj cat az://container/blobname
    $ obj cat gs://bucket/blobname
    $ obj cat s3://bucket/blobname
    $ obj cat file:/path
    $ cat file | obj put gs://bucket/blobname
```

# Python Usage

Accessing blobs from Python is easy: the two functions you need to know
are:

- `gopen`: opens a stream with standard Python filemodes; shortcuts for files
- `objopen`: opens a stream with `objio` verbs; uses `file:` rule for files

```Python
    import objio

    with objio.gopen("gs://bucket/blob", "rb") as stream:
        contents = stream.read()

    with objio.openobj("gs://bucket/blob", "read") as stream:
        contents = stream.read()

    with objio.openobj("gs://bucket/", "list") as stream:
        files = stream.read().split("\n")
```
