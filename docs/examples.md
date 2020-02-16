# Examples


```python
%cd ..
```

    /home/tmb/exp/objio



```python
import sys
import objio
```

## Python API

Let's read a file from Google cloud storage using `objio.gopen` (generic open):


```python
url = "gs://lpr-openimages/openimages-shard.ipynb"
with objio.gopen(url, "r") as stream:
    print(stream.read(100))
```

    b'{\n "cells": [\n  {\n   "cell_type": "code",\n   "execution_count": 1,\n   "metadata": {},\n   "outputs": '


The same code works for local files:


```python
url = "file:/usr/share/dict/words"
with objio.gopen(url, "r") as stream:
    print(stream.read(20))
```

    A
    A's
    AMD
    AMD's
    AOL
    


When no URL scheme is given, `gopen` just defaults to regular `open`:


```python
url = "/usr/share/dict/words"
with objio.gopen(url, "r") as stream:
    print(stream.read(20))
```

    A
    A's
    AMD
    AMD's
    AOL
    


There is an alternative library interface called `objio.objopen` that supports additional "verbs". The "read" and "write" verbs correspond to "r" and "w", and "list" generates a newline separated listing of absolute URLs of all objects in a bucket.

In addition, `objopen` always uses a subprocess for I/O and always returns an `objio.Pipe` object that supports the `wait(timeout=sec)` method to wait for a subprocess to finish.


```python
url = "file:/usr/share/dict/words"
stream = objio.objopen(url, "read")
data = stream.read()
stream.close(timeout=10.0)
print(data[:10])
```

    b"A\nA's\nAMD\n"



```python
url = "file:/usr/share/dict"
stream = objio.objopen(url, "list")
data = stream.read()
stream.close(timeout=10.0)
print(data[:50])
```

    b'/usr/share/dict/README.select-wordlist\n/usr/share/'


## Command Line

The library defines a single toplevel command called `obj`. It supports subcommands of `cat`, `put`, `list`, `auth`, and `handler`.


```python
!obj cat http://www.google.com | fmt | sed 3q
```

    <!doctype html><html itemscope="" itemtype="http://schema.org/WebPage"
    lang="en"><head><meta content="Search the world's information,
    including webpages, images, videos and more. Google has many
    fmt: write error: Broken pipe



```python
!obj cat gs://lpr-openimages/openimages-train-000000.tar | tar -tvf - | sed 5q
```

    -r--r--r-- bigdata/bigdata 180172 2020-02-12 16:21 e39871fd9fd74f55.jpg
    -r--r--r-- bigdata/bigdata    816 2020-02-12 16:21 e39871fd9fd74f55.json
    -r--r--r-- bigdata/bigdata  88910 2020-02-12 16:21 f18b91585c4d3f3e.jpg
    -r--r--r-- bigdata/bigdata   2719 2020-02-12 16:21 f18b91585c4d3f3e.json
    -r--r--r-- bigdata/bigdata  84559 2020-02-12 16:21 ede6e66b2fb59aab.jpg
    tar: write error



```python
!obj list gs://lpr-openimages | sed 10q
```

    gs://lpr-openimages/openimages-shard.ipynb
    gs://lpr-openimages/openimages-train-000000.tar
    gs://lpr-openimages/openimages-train-000001.tar
    gs://lpr-openimages/openimages-train-000002.tar
    gs://lpr-openimages/openimages-train-000003.tar
    gs://lpr-openimages/openimages-train-000004.tar
    gs://lpr-openimages/openimages-train-000005.tar
    gs://lpr-openimages/openimages-train-000006.tar
    gs://lpr-openimages/openimages-train-000007.tar
    gs://lpr-openimages/openimages-train-000008.tar


## Configurability and New Protocols

Internally, `obj` handles all object access by calling command line programs. This is easy to configure and adapt to new protocols. In addition, since Python is not very good at multithreading, this is actually a good solution, since I/O happens asynchronously. In fact, `obj` will try to plumb the output from the command line program directly to `stdout` so that I/O is as efficient as if the command line program had been called directly.

You can see the commands that `obj` invokes by using the `handler` subcommand.


```python
!obj handler file: --verb=read
```

    cmd: [dd, 'if={path}', bs=4M]


Let's say you want to change this default to using `cat`. You can define the handler for a protocol with a small YAML file.


```python
%%writefile objio.yml
schemes:
  file:
    read:
      cmd: ["cat", "{path}"]
```

    Overwriting objio.yml



```python
!obj handler file: --verb=read
```

    cmd: [cat, '{path}']



```python
!obj cat file:/usr/share/dict/words | sed 3q
```

    A
    A's
    AMD

