#!/usr/bin/python3
#
# Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
# This file is part of webloader (see TBD).
# See the LICENSE file for licensing terms (BSD-style).
#

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

bufsize = 8192

env_prefix = "OBJIO_"

default = """
schemes:
  file:
    read:
        cmd: ["dd", "if={path}", "bs=4M"]
    write:
        cmd: ["dd", "if=-", "of={path}", "bs=4M"]
  gs:
    read:
        cmd: ["gsutil", "cat", "{url}"]
    write:
        cmd: ["gsutil", "cp", "{url}"]
  http:
    read:
        cmd: ["curl", "--fail", "-L", "-s", "{url}", "--output", "-"]
  https:
    read:
        cmd: ["curl", "--fail", "-L", "-s", "{url}", "--output", "-"]
  az:
    read:
        cmd: "az storage blob download --container-name '{bucket}' --name '{nobucket}' --file -"
"""

with io.StringIO(default) as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

def update_yaml_with(target, source):
    if isinstance(target, dict) and isinstance(source, dict):
        for k, v in source.items():
            if k not in target:
                target[k] = v
            else:
                target[k] = merge(target[k], v)
    return target

env_vars = [
    (env_prefix+"GLOBAL", os.path.expanduser("~/.objio.yml")),
    (env_prefix+"LOCAL", "./objio.yml")
]

top_level = set("commands".split())
scheme_level = set("read write list delete stat".split())
handler_level = set("cmd class errors".split())

for var, default in env_vars:
    path = os.environ.get(var, default)
    if path is not None and os.path.exists(path):
        with open(path) as stream:
            updates = yaml.load(path, Loader=yaml.FullLoader)
            update_yaml_with(config, updates)

if int(os.environ.get("gopen_debug", 0)):
    yaml.dump(config, sys.stderr)

class GopenException(Exception):
    def __init__(self, info):
        super().__init__()
        self.info = info

class Pipe(object):
    def __init__(self, *args, mode="r", raise_errors=True, direct=False, **kw):
        self.raise_errors = raise_errors
        self.direct = direct
        self.mode = mode
        self.open(*args, **kw)
    def open(self, *args, **kw):
        mode = self.mode
        if self.direct:
            if mode[0] == "w":
                if "b" in mode:
                    stdin = sys.stdin.buffer
                else:
                    stdin = sys.stdin
                stdout = None
            if mode[0] == "r":
                if "b" in mode:
                    stdout = sys.stdout.buffer
                else:
                    stdout = sys.stdout
                stdin = None
        else:
            if mode[0] == "r":
                stdin = subprocess.PIPE
                stdout = None
            elif mode[0] == "w":
                stdout = subprocess.PIPE
                stdin = None
        self.proc = subprocess.Popen(*args, bufsize=bufsize, stdin=stdin, stdout=stdout, **kw)
        self.args = (args, kw)
        if mode == "w":
            self.stream = self.proc.stdin
        elif "r" in mode:
            self.stream = self.proc.stdout
        if not self.direct and self.stream is None:
            print(self.direct)
            raise GopenException(f"{self.args}: no stream (open)")
        else:
            self.stream = None
        self.status = None
        return self
    def write(self, *args, **kw):
        result = self.stream.write(*args, **kw)
        self.status = self.proc.poll()
        if self.status is not None:
            self.status = self.proc.wait()
            if self.status != 0 and self.raise_errors:
                raise GopenException(f"{self.args}: exit {self.status} (write)")
    def read(self, *args, **kw):
        result = self.stream.read(*args, **kw)
        self.status = self.proc.poll()
        if self.status is not None:
            self.status = self.proc.wait()
            if self.status != 0 and self.raise_errors:
                raise GopenException(f"{self.args}: exit {self.status} (read)")
        return result
    def readLine(self, *args, **kw):
        result = self.stream.readLine(*args, **kw)
        self.status = self.proc.poll()
        if self.status is not None:
            self.status = self.proc.wait()
            if self.status != 0 and self.raise_errors:
                raise GopenException(f"{self.args}: exit {self.status} (readLine)")
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
                raise GopenException(f"{self.args}: exit {self.status} (close)")
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.close()

def maybe(f, default):
    try:
        return f()
    except:
        return default

def shell_handler(url, pr, mode, raise_errors=True, direct=False):
    kw = dict(
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
        bucket=maybe(lambda:pr.path.split("/")[1], ""),
        nobucket=maybe(lambda:pr.path.split("/")[2:], ""),
        dirname=os.path.dirname(pr.path),
        filename=os.path.basename(pr.path),
        port=pr.port
    )
    schemes = config.get("schemes")
    scheme = schemes.get(pr.scheme)
    if scheme is None:
        raise ValueError(f"objio: {url}: no handler found for {pr.scheme}"+
                         " (known: " + " ".join(schemes.keys())+")")
    if mode[0]=="r":
        handler = scheme.get("read")
    elif mode[0]=="w":
        handler = scheme.get("write")
    if scheme is None:
        raise ValueError(f"objio: {url}: no handler found for {pr.scheme}, mode {mode}"+
                         yaml.dump(handler))
    cmd = handler.get("cmd")
    if cmd is None:
        raise ValueError(f"objio: {url}: no command specified for {pr.scheme}, mode {mode}\n"+
                         yaml.dump(handler))
    if handler.get("substitute", True):
        if isinstance(cmd, list):
            cmd = [s.format(**kw) for s in cmd]
        elif isinstance(cmd, str):
            cmd = cmd.format(**kw)
        else:
            raise ValueError(f"cmd: {cmd}: wrong type")
    if int(os.environ.get(env_prefix+"gopen_debug", "0")):
        print("#", cmd, file=sys.stderr)
    if isinstance(cmd, str):
        return Pipe(cmd, shell=True, mode=mode, direct=direct)
    elif isinstance(cmd, list):
        return Pipe(cmd, mode=mode, raise_errors=True, direct=direct)

def gopen(url, mode="rb", direct=False):
    if url == "-":
        if "w" in mode:
            stream = sys.stdout
        else:
            stream = sys.stdin
        if "b" in mode:
            stream = stream.buffer
        return stream
    pr = urlparse(url)
    if pr.scheme=="":
        return open(url, mode)
    else:
        return shell_handler(url, pr, mode, direct=direct)
