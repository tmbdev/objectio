
# obj (command)


## obj auth (subcommand)

```generic
Usage: obj auth [OPTIONS] URL

  Authenticate to the server for the URL.

  This either runs an interactive command to permit the user to
  authenticate, or prints an explanation of how to authenticate.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```


## obj buckets (subcommand)

```generic
Usage: obj buckets [OPTIONS] URL

  List all available buckets for the currently authenticated user.

  Provides a list of toplevel buckets. On file systems, provides a list of
  volumes.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```


## obj cat (subcommand)

```generic
Usage: obj cat [OPTIONS] URL

  Cat the given object to stdout.

  The object is opened using the configured cloud command and the output is
  piped directly to standard out.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```


## obj handler (subcommand)

```generic
Usage: obj handler [OPTIONS] URL

  Output the handlers for a given URL and verb.

  Looks in the configuration file for a handler for the combination of the
  URL and verb and outputs it in YAML format. This is mainly intended for
  debugging configuration file issues.

Options:
  --verb TEXT
  --help       Show this message and exit.
```


## obj list (subcommand)

```generic
Usage: obj list [OPTIONS] URL

  List the objects in the given bucket or at the given path.

  The output is a list of absolute urls that are usable with `cat.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```


## obj put (subcommand)

```generic
Usage: obj put [OPTIONS] URL

  Upload stdin to the given location.

  The input is uploaded to the server at the given location. Most (but not
  all) object stores will only update the store after a successful update.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

