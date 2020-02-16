# obj (command)
```generic
Usage: obj [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  auth     Authenticate to the server for the URL.
  buckets  List all available buckets for the currently authenticated user.
  cat      Cat the given object to stdout.
  handler
  list     List the objects in the given bucket or at the given path.
  put      Upload stdin to the given location.
```

# obj auth (sub-command)
```generic
Usage: obj auth [OPTIONS] URL

  Authenticate to the server for the URL.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

# obj buckets (sub-command)
```generic
Usage: obj buckets [OPTIONS] URL

  List all available buckets for the currently authenticated user.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

# obj cat (sub-command)
```generic
Usage: obj cat [OPTIONS] URL

  Cat the given object to stdout.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

# obj handler (sub-command)
```generic
Usage: obj handler [OPTIONS] URL

Options:
  --verb TEXT
  --help       Show this message and exit.
```

# obj list (sub-command)
```generic
Usage: obj list [OPTIONS] URL

  List the objects in the given bucket or at the given path.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

# obj put (sub-command)
```generic
Usage: obj put [OPTIONS] URL

  Upload stdin to the given location.

Options:
  --timeout FLOAT
  --help           Show this message and exit.
```

