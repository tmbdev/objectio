Usage information for command line programs.
# obj (command)

```
Usage: obj [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  auth     Authenticate to the server for the URL.
  buckets  List all available buckets for the currently authenticated user.
  cat      Cat the given object to stdout.
  config   Output the entire config file.
  handler  Output the handlers for a given URL and verb.
  list     List the objects in the given bucket or at the given path.
  put      Upload stdin to the given location.
```

## obj auth (subcommand)

```
Usage: obj auth [OPTIONS] URL

  Authenticate to the server for the URL.

  This either runs an interactive command to permit the user to
  authenticate, or prints an explanation of how to authenticate.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

## obj buckets (subcommand)

```
Usage: obj buckets [OPTIONS] URL

  List all available buckets for the currently authenticated user.

  Provides a list of toplevel buckets. On file systems, provides a list of
  volumes.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

## obj cat (subcommand)

```
Usage: obj cat [OPTIONS] URL

  Cat the given object to stdout.

  The object is opened using the configured cloud command and the output is
  piped directly to standard out.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

## obj config (subcommand)

```
Usage: obj config [OPTIONS]

  Output the entire config file.

Options:
  --help  Show this message and exit.
```

## obj handler (subcommand)

```
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

```
Usage: obj list [OPTIONS] URL

  List the objects in the given bucket or at the given path.

  The output is a list of absolute urls that are usable with `cat.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

## obj put (subcommand)

```
Usage: obj put [OPTIONS] URL

  Upload stdin to the given location.

  The input is uploaded to the server at the given location. Most (but not
  all) object stores will only update the store after a successful update.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

