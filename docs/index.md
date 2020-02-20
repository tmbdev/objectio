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

```Python
    import objio

    stream = objio.gopen("gs://bucket/blob", "rb")
```

# Configuration

The `objio` library is intended to be just a simple wrapper around
existing command line programs. You can configure how command line programs
are invoked with a YAML configuration file. Configurations are a combination
of the built-in defaults with global and directory-local overrides.
You can specify a list of ":"-separated YAML files to load from with the
`OBJIO_PATH` variable. By default, it will look in

```Bash
OBJIO_PATH=/usr/local/etc/objio.yaml:~/.objio.yaml:./objio.yaml
OBJIO_PATH=$OBJIO_PATH:/usr/local/etc/objio.yml:~/.objio.yml:./objio.yml
```

The configuration file contains command specifications, either as strings
(passed to Bash for execution) or as lists (executed directly). You can override
any URL schema, and create new ones for new functionality:

```YAML
    schemes:
        http_buffered:
            read:
                cmd: "curl --fail -L -s '{url}' --output - | mbuffer"
        random:
            read:
                cmd: ["cat", "/dev/random"]
```

After putting these definitions into `./objio.yaml`, you can say:

```Bash
    $ obj cat http_buffered://storage.googleapis.com/bucket/data
    $ obj cat random:
```

The following variables are available for substitution inside `{...}`:

- url, scheme, netloc, path, params, query, fragment, username, password, hostname, port: same meaning as in `urllib.parse`
- firstdir: first element of path
- restdirs: everything but first element of path
- dirname: everything but last element of path
- filename: last element of path

Note that Google and S3 put the actual bucket name into the
`netloc` variable; that is, their syntax is `gs://bucket/object`, not
`gs:/bucket/object`, which might be more logical.

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

# Development

## Tools

For development, we're using the following Python tools:

- Packaging: setuptools wheel
- Testing: pytest (also: coverage tox)
- Uploading to PyPI: twine keyring
- Documentation generation: mkdocs pydoc-markdown jupyter nbconvert

This is a fairly minimalist set of tools for modern Python packaging.

Custom scripts:

- Automation: Makefile
- Documentation generation: gendocs
- Testing on Docker: dockergit dockerpip

## Configuration Files

Configuration:

- requirements for virtual environment: requirements.txt
- requirements for pip install: setup.py
- requirements for development: requirements.dev.txt

Makefile targets

- tests: run unit tests
- venv: setup the virtualenv
- push: push to github
- dist: make a distribution on PyPI
- docs: build the docs
- clean: clean temporary files, build artifacts
- passwd: authenticate to keyring
