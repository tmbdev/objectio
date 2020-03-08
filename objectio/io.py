#!/usr/bin/python
#
# Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
# This file is part of the objectio library.
# See the LICENSE file for licensing terms (BSD-style).
#

__all__ = "objopen gopen config".split()

import os
import sys
import time
import subprocess
import yaml
import io
from urllib.parse import urlparse

from .checks import checkmember, checktype

ENV_PREFIX = "objectio_"

objectio_DEBUG = int(os.environ.get(ENV_PREFIX+"DEBUG", "0"))

objectio_PATH = "/usr/local/etc/objectio.yaml:~/.objectio.yaml:./objectio.yaml"
objectio_PATH += ":" + objectio_PATH.replace("yaml", "yml")
objectio_PATH = os.environ.get(ENV_PREFIX+"PATH", objectio_PATH)

if objectio_DEBUG:
    print(f"# objectio path: {objectio_PATH}", file=sys.stderr)

# FIXME: move defaults into a separate, installable file

DEFAULT_CONFIG = """
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

with io.StringIO(DEFAULT_CONFIG) as stream:
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

# load YAML config files


for path in objectio_PATH.split(":"):
    if os.path.exists(path):
        if objectio_DEBUG:
            print(f"objectio updating config with {path}", file=sys.stderr)
        with open(path) as stream:
            updates = yaml.load(stream, Loader=yaml.FullLoader)
            config = update_yaml_with(config, updates)

if objectio_DEBUG:
    yaml.dump(config, sys.stderr)


checkmember("schemes", list(config.keys()), "config file error")


class objectioExeption(Exception):
    """I/O Exceptions during objectio operations."""
    def __init__(self, info):
        super().__init__()
        self.info = info


class Pipe:
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
                raise objectioExeption(f"{cmd}: no stream (open)")
        self.status = None

    def check_status(self):
        self.status = self.proc.poll()
        self.handle_status()

    def handle_status(self):
        if self.status is not None:
            self.status = self.proc.wait()
            if self.status != 0 and not self.ignore_errors:
                raise objectioExeption(f"{self.args}: exit {self.status} (write)")

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

    def __exit__(self, etype, value, traceback):
        self.close()


def maybe(f, default):
    """Evaluate f and return the value; return default on error."""
    try:
        return f()
    except:  # noqa: E722
        return default


def get_handler_for(url, verb):
    """Look for a handler for the url/verb combination in the config file."""
    checkmember(verb, "read write delete list auth buckets")
    pr = urlparse(url)
    schemes = config.get("schemes")
    scheme = schemes.get(pr.scheme)
    if scheme is None:
        raise ValueError(f"objectio: {url}: no handler found for {pr.scheme}" +
                         " (known: " + " ".join(schemes.keys())+")")
    handler = scheme.get(verb)
    if handler is None:
        raise ValueError(f"objectio: {url}: no handler found for {pr.scheme}, verb {verb}" +
                         yaml.dump(handler))
    return handler


def url_variables(url, pr):
    """Generate a dictionary exposing the URL components. Names follow urlparse."""
    result = dict(pr._asdict(),
                  url=url,
                  firstdir=maybe(lambda: pr.path.split("/")[1], ""),
                  restdirs=maybe(lambda: "/".join(pr.path.split("/")[2:]), ""),
                  dirname=os.path.dirname(pr.path),
                  filename=os.path.basename(pr.path))
    if pr.scheme == "file":
        result["abspath"] = os.path.abspath(pr.path)
    return result


def substitute_variables(cmd, variables):
    """Given a cmd (str, list), substitute variables in it."""
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
        raise ValueError(f"objectio: {url}: no command specified for verb {verb}\n" +
                         yaml.dump(handler))
    message = handler.get("message")
    if message is not None:
        print(f"{verb} for {url}:\n")
        print(message, file=sys.stderr)
        return None
    cmd = handler.get("cmd")
    if cmd is None:
        raise ValueError("{url}: config neither specifies message: nor cmd:")
    pr = urlparse(url)
    if handler.get("substitute", True):
        cmd = substitute_variables(cmd, url_variables(url, pr))
    if objectio_DEBUG or verbose:
        print("#", cmd, file=sys.stderr)
    if isinstance(cmd, str):
        cmd = ["/bin/bash", "-c", cmd]
    checktype(cmd, (list, tuple))
    return Pipe(cmd, writable(verb), ignore_errors=ignore_errors, stream=stream)


def objopen(url, verb="read", stream=None):
    """Open a storage object. This always spawns a subprocess and supports all verbs."""
    pr = urlparse(url)
    if pr.scheme == "":
        url = "file:"+url
    return cmd_handler(url, verb, stream=stream)


def gopen(url, filemode="rb"):
    """Open a storage object, with standard file modes and local files."""
    if url == "-":
        stream = {"r": sys.stdout, "w": sys.stdin}[filemode[0]]
        if "b" in filemode:
            stream = stream.buffer
        return stream
    pr = urlparse(url)
    if pr.scheme == "":
        return open(url, filemode)
    elif pr.scheme == "file":
        return open(pr.path, filemode)
    verb = {"r": "read", "w": "write"}[filemode[0]]
    return cmd_handler(url, verb)
