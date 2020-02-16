#!/usr/bin/python3
#
# Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
# This file is part of webloader (see TBD).
# See the LICENSE file for licensing terms (BSD-style).
#

"""Object Store I/O Functions.

This defines two functions (`gopen`, `objopen`) that can access a 
large variety of object stores using a uniform interface.
"""

__all__ = "objopen gopen config".split()

import os
import sys
import argparse
import time
from itertools import islice
import subprocess
import braceexpand
import re
import yaml
import io
from urllib.parse import urlparse

env_prefix = "OBJIO_"
objio_debug = int(os.environ.get(env_prefix+"DEBUG", "0"))
if objio_debug:
    print("objio DEBUG mode", file=sys.stderr)

# FIXME: move defaults into a separate, installable file

default = """
config:

  bufsize: 8192

schemes:

  file:
    read:
      cmd: ["dd", "if={path}", "bs=4M"]
    write:
      cmd: ["dd", "of={path}", "bs=4M"]
    list:
      cmd: "ls -1d {abspath}/*"
    buckets:
      cmd: "mount | awk '/^\\\\/dev\\\\/sd/{print $3}'"
      substitute: false
    auth: 
      message: |
        No authentication for local files.
        
  gs:
    read:
        cmd: ["gsutil", "cat", "{url}"]
    write:
        cmd: ["gsutil", "cp", "-", "{url}"]
    buckets:
        cmd: ["gsutil", "ls"]
    list:
        cmd: ["gsutil", "ls", "{url}"]
    auth: 
      message: |
        Use "gcloud auth login" to authenticate.

  http:
    read:
        cmd: ["curl", "--fail", "-L", "-s", "{url}", "--output", "-"]

  https:
    read:
        cmd: ["curl", "--fail", "-L", "-s", "{url}", "--output", "-"]

  az:
    read:
        cmd: "az storage blob download --container-name '{netloc}' --name '{path}' --file -"
    buckets:
        cmd: "az storage container list"
    list:
        cmd: "az storage blob list --container-name '{netloc}'"
"""

with io.StringIO(default) as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

def update_yaml_with(target, source):
    """Merge the source YAML tree into the target. Useful for merging config files."""
    if isinstance(target, dict) and isinstance(source, dict):
        for k, v in source.items():
            if k not in target:
                target[k] = v
            else:
                target[k] = update_yaml_with(target[k], v)
    return source

env_vars = [
    (env_prefix+"SYSTEM", "/usr/local/etc/objio.yaml"),
    (env_prefix+"USER", os.path.expanduser("~/.objio.yml")),
    (env_prefix+"LOCAL", "./objio.yml")
]

# load YAML config files

for var, default in env_vars:
    path = os.environ.get(var, default)
    if path is not None and os.path.exists(path):
        if objio_debug:
            print(f"objio updating config with {path}", file=sys.stderr)
        with open(path) as stream:
            updates = yaml.load(stream, Loader=yaml.FullLoader)
            config = update_yaml_with(config, updates)

if objio_debug:
    yaml.dump(config, sys.stderr)

class ObjioExeption(Exception):
    """I/O Exceptions during objio operations."""
    def __init__(self, info):
        super().__init__()
        self.info = info

class Pipe(object):
    """A wrapper for the pipe class that adapts it to the needs of objio."""
    def __init__(self, cmd, writable, raise_errors=True, stream=None, bufsize=8192, **kw):
        assert isinstance(cmd, list)
        self.args = (cmd, writable)
        self.raise_errors = raise_errors
        stdin = stdout = None
        if writable:
            stdin = stream or subprocess.PIPE
        else:
            stdout = stream or subprocess.PIPE
        self.proc = subprocess.Popen(cmd, bufsize=bufsize, stdin=stdin, stdout=stdout, **kw)
        self.stream = None
        if not stream:
            self.stream = self.proc.stdin if writable else self.proc.stdout
            if self.stream is None:
                raise ObjioExeption(f"{cmd}: no stream (open)")
        self.status = None
    def write(self, *args, **kw):
        result = self.stream.write(*args, **kw)
        self.status = self.proc.poll()
        if self.status is not None:
            self.status = self.proc.wait()
            if self.status != 0 and self.raise_errors:
                raise ObjioExeption(f"{self.args}: exit {self.status} (write)")
    def read(self, *args, **kw):
        result = self.stream.read(*args, **kw)
        self.status = self.proc.poll()
        if self.status is not None:
            self.status = self.proc.wait()
            if self.status != 0 and self.raise_errors:
                raise ObjioExeption(f"{self.args}: exit {self.status} (read)")
        return result
    def readLine(self, *args, **kw):
        result = self.stream.readLine(*args, **kw)
        self.status = self.proc.poll()
        if self.status is not None:
            self.status = self.proc.wait()
            if self.status != 0 and self.raise_errors:
                raise ObjioExeption(f"{self.args}: exit {self.status} (readLine)")
    def wait(self, timeout=3600.0):
        self.proc.wait(timeout)
    def close(self, timeout=3600.0):
        if self.stream is not None:
            self.stream.close()
        try:
            self.status = self.proc.wait(timeout)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            time.sleep(0.1)
            self.proc.kill()
            self.status = self.proc.wait(1.0)
        if self.raise_errors == "all":
            if self.status != 0 and self.raise_errors:
                raise ObjioExeption(f"{self.args}: exit {self.status} (close)")
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.close()

def maybe(f, default):
    """Evaluate f and return the value; return default on error."""
    try:
        return f()
    except:
        return default

def get_handler_for(url, verb):
    """Look for a handler for the url/verb combination in the config file."""
    assert verb in "read write delete list auth buckets".split(), f"{verb} not one of the accepted modes"
    pr = urlparse(url)
    schemes = config.get("schemes")
    scheme = schemes.get(pr.scheme)
    if scheme is None:
        raise ValueError(f"objio: {url}: no handler found for {pr.scheme}"+
                         " (known: " + " ".join(schemes.keys())+")")
    handler = scheme.get(verb)
    if handler is None:
        raise ValueError(f"objio: {url}: no handler found for {pr.scheme}, verb {verb}"+
                         yaml.dump(handler))
    return handler

def url_variables(url, pr):
    """Generate a dictionary exposing the URL components. Names follow urlparse."""
    result = dict(
        url=url,
        scheme=pr.scheme,
        netloc=pr.netloc,
        path=pr.path,
        params=pr.params,
        query=pr.query,
        fragment=pr.fragment,
        username=pr.username,
        password=pr.password,
        hostname=pr.hostname,
        firstdir=maybe(lambda:pr.path.split("/")[1], ""),
        restdirs=maybe(lambda:"/".join(pr.path.split("/")[2:]), ""),
        dirname=os.path.dirname(pr.path),
        filename=os.path.basename(pr.path),
        port=pr.port
    )
    if pr.scheme=="file":
        result["abspath"] = os.path.abspath(pr.path)
    return result

def substitute_variables(cmd, variables):
    """Given a cmd specified either as a string or as a list, substitute the variables."""
    if isinstance(cmd, list):
        return [s.format(**variables) for s in cmd]
    elif isinstance(cmd, str):
        return cmd.format(**variables)
    else:
        raise ValueError(f"cmd: {cmd}: wrong type")

def writable(verb):
    """Does the given verb require a writable file descriptor?"""
    return verb == "write"

def cmd_handler(url, verb, raise_errors=True, stream=None, verbose=False):
    """Given a url and verb, find the command handler."""
    handler = get_handler_for(url, verb)
    if handler is None:
        raise ValueError(f"objio: {url}: no command specified for {pr.scheme}, verb {verb}\n"+
                         yaml.dump(handler))
    message = handler.get("message")
    if message is not None:
        print(f"{verb} for {url}:\n")
        print(message, file=sys.stderr)
        return
    cmd = handler.get("cmd")
    if cmd is None:
        raise ValueError("{url}: config neither specifies message: nor cmd:")
    pr = urlparse(url)
    if handler.get("substitute", True):
        cmd = substitute_variables(cmd, url_variables(url, pr))
    if objio_debug or verbose:
        print("#", cmd, file=sys.stderr)
    if isinstance(cmd, str):
        cmd = ["/bin/bash", "-c", cmd]
    assert isinstance(cmd, (list, tuple))
    return Pipe(cmd, writable(verb), raise_errors=True, stream=stream)

def objopen(url, verb="read", stream=None):
    """Open a storage object. This always spawns a subprocess and supports all verbs."""
    pr = urlparse(url)
    if pr.scheme == "":
        url = "file:"+url
    return cmd_handler(url, verb, stream=stream)

def gopen(url, filemode="rb"):
    """Open a storage object. This shortcuts to open() for local files and accepts file open modes."""
    if url == "-":
        stream = {"r": sys.stdout, "w": sys.stdin}[filemode[0]]
        if "b" in filemode:
            stream = stream.buffer
        return stream
    pr = urlparse(url)
    if pr.scheme=="":
        return open(url, filemode)
    elif pr.scheme=="file":
        return open(pr.path, filemode)
    verb = {"r": "read", "w": "write"}[filemode[0]]
    return cmd_handler(url, verb)
