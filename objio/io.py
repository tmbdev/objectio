
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

objio_path = "/usr/local/etc/objio.yaml:~/.objio.yaml:./objio.yaml"
objio_path += ":" + objio_path.replace("yaml", "yml")
objio_path = os.environ.get(env_prefix+"PATH", objio_path)

if objio_debug:
    print(f"# objio path: {objio_path}", file=sys.stderr)

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

def checktype(value, types, msg=""):
    """Type check value; raise ValueError if fails."""
    if not isinstance(value, types):
        raise ValueError(f"ERROR {msg}: {value} should be of type {types}")


def checkmember(value, values, msg=""):
    """Check value for membership; raise ValueError if fails."""
    if value not in values:
        raise ValueError(f"ERROR {msg}: {value} should be in {values}")


def checkrange(value, lo, hi, msg=""):
    """Check value for membership; raise ValueError if fails."""
    if value < lo or value > hi:
        raise ValueError(f"ERROR {msg}: {value} should be in range {lo} {hi}")


def update_yaml_with(target, source):
    """Merge the source YAML tree into the target. Useful for merging config files."""
    if isinstance(target, dict) and isinstance(source, dict):
        for k, v in source.items():
            if k not in target:
                target[k] = v
            else:
                target[k] = update_yaml_with(target[k], v)
    return source

# load YAML config files

for path in objio_path.split(":"):
    if os.path.exists(path):
        if objio_debug:
            print(f"objio updating config with {path}", file=sys.stderr)
        with open(path) as stream:
            updates = yaml.load(stream, Loader=yaml.FullLoader)
            config = update_yaml_with(config, updates)

if objio_debug:
    yaml.dump(config, sys.stderr)

checkmember("schemes", list(config.keys()), "config file error")

class ObjioExeption(Exception):
    """I/O Exceptions during objio operations."""
    def __init__(self, info):
        super().__init__()
        self.info = info

class Pipe(object):
    """A wrapper for the subproces.Pipe class that checks status on read/write."""
    def __init__(self, cmd, writable, ignore_errors=False, stream=None, bufsize=8192, timeout=60.0, **kw):
        checktype(cmd, list)
        self.timeout = timeout
        self.args = (cmd, writable)
        self.ignore_errors = ignore_errors
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
    def check_status(self):
        self.status = self.proc.poll()
        self.handle_status()
    def handle_status(self):
        if self.status is not None:
            self.status = self.proc.wait()
            if self.status != 0 and not self.ignore_errors:
                raise ObjioExeption(f"{self.args}: exit {self.status} (write)")
    def write(self, *args, **kw):
        result = self.stream.write(*args, **kw)
        self.check_status()
        return result
    def read(self, *args, **kw):
        result = self.stream.read(*args, **kw)
        self.check_status()
        return result
    def readLine(self, *args, **kw):
        result = self.stream.readLine(*args, **kw)
        self.check_status()
        return result
    def wait(self, timeout=None):
        timeout = timeout or self.timeout
        try:
            self.status = self.proc.wait(timeout)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            time.sleep(0.1)
            self.proc.kill()
            self.status = self.proc.wait(1.0)
        self.check_status()
    def close(self, timeout=None):
        if self.stream is not None:
            self.stream.close()
        self.wait(timeout)
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
    checkmember(verb, "read write delete list auth buckets")
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
    result = dict(pr._asdict(),
                  url=url,
                  firstdir=maybe(lambda:pr.path.split("/")[1], ""),
                  restdirs=maybe(lambda:"/".join(pr.path.split("/")[2:]), ""),
                  dirname=os.path.dirname(pr.path),
                  filename=os.path.basename(pr.path))
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

def cmd_handler(url, verb, ignore_errors=False, stream=None, verbose=False):
    """Given a url and verb, find the command handler."""
    handler = get_handler_for(url, verb)
    if handler is None:
        raise ValueError(f"objio: {url}: no command specified for verb {verb}\n"+
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
    checktype(cmd, (list, tuple))
    return Pipe(cmd, writable(verb), ignore_errors=True, stream=stream)

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
