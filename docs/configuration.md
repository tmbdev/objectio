# Configuration and New Protocols

The `objectio` library is intended to be just a simple wrapper around
existing command line programs. You can configure how command line programs
are invoked with a YAML configuration file. Configurations are a combination
of the built-in defaults with global and directory-local overrides.
You can specify a list of ":"-separated YAML files to load from with the
`objectio_PATH` variable. By default, it will look in

```Bash
objectio_PATH=/usr/local/etc/objectio.yaml:~/.objectio.yaml:./objectio.yaml
objectio_PATH=$objectio_PATH:/usr/local/etc/objectio.yml:~/.objectio.yml:./objectio.yml
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

After putting these definitions into `./objectio.yaml`, you can say:

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

