
#
# Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
# This file is part of webloader (see TBD).
# See the LICENSE file for licensing terms (BSD-style).
#
from __future__ import unicode_literals

import sys
import objectio
import yaml
import io

testcases = yaml.load(io.StringIO("""
read:
  - url: https://lpr-openimages.storage.googleapis.com/openimages-shard.ipynb
    contains: with wds.ShardWriter
list:
  - url: file:/etc
    contains: passwd
write:
  - bucket: file:/tmp
"""), Loader=yaml.FullLoader)


def test_objopen_read():
    for case in testcases["read"]:
        print("# testing", case["url"], file=sys.stderr)
        with objectio.objopen(case["url"], "read") as stream:
            text = stream.read().decode("utf-8")
        assert case["contains"] in text


def test_objopen_list():
    for case in testcases["list"]:
        print("# testing", case["url"], file=sys.stderr)
        with objectio.objopen(case["url"], "list") as stream:
            text = stream.read().decode("utf-8")
        assert case["contains"] in text


def test_objopen_write():
    original = "hello world"
    for case in testcases["write"]:
        fname = case["bucket"] + "/test.txt"
        print("# testing", fname, file=sys.stderr)
        with objectio.objopen(fname, "write") as stream:
            stream.write(original.encode("utf-8"))
        with objectio.objopen(fname, "read") as stream:
            text = stream.read().decode("utf-8")
        assert text == original


def test_gopen_file(tmp_path):
    fname = str(tmp_path / "test.txt")
    original = "hello world"
    with objectio.gopen(fname, "w") as stream:
        stream.write(original)
    with objectio.gopen(fname, "r") as stream:
        text = stream.read()
    assert text == original
