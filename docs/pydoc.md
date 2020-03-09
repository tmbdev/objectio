
# Module `objectio.__init__`

```
Help on module objectio.__init__ in objectio:

NAME
    objectio.__init__

FILE
    /home/tmb/proj/objectio/objectio/__init__.py



```

# Module `objectio.checks`

```
Help on module objectio.checks in objectio:

NAME
    objectio.checks

DESCRIPTION
    # Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
    # This file is part of the objectio  library.
    # See the LICENSE file for licensing terms (BSD-style).
    #

FUNCTIONS
    checkmember(value, values, msg='')
        Check value for membership; raise ValueError if fails.
    
    checkrange(value, lo, hi, msg='')
        Check value for membership; raise ValueError if fails.
    
    checktype(value, types, msg='')
        Type check value; raise ValueError if fails.

FILE
    /home/tmb/proj/objectio/objectio/checks.py



```

# Module `objectio.io`

```
Help on module objectio.io in objectio:

NAME
    objectio.io

DESCRIPTION
    # Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
    # This file is part of the objectio library.
    # See the LICENSE file for licensing terms (BSD-style).
    #

FUNCTIONS
    gopen(url, filemode='rb')
        Open a storage object, with standard file modes and local files.
    
    objopen(url, verb='read', stream=None)
        Open a storage object. This always spawns a subprocess and supports all verbs.

DATA
    __all__ = ['objopen', 'gopen', 'config']
    config = {'config': {'bufsize': 8192}, 'schemes': {'az': {'buckets': {...

FILE
    /home/tmb/proj/objectio/objectio/io.py



```
