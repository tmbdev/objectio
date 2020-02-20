#
# Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
# This file is part of webloader (see TBD).
# See the LICENSE file for licensing terms (BSD-style).
#
from __future__ import unicode_literals

import subprocess


def run(script, *args):
    result = subprocess.check_output(["/bin/bash", "-c", script]).decode("utf-8")
    for arg in args:
        assert arg in result, (arg, result)


def test_obj():
    run("python3 ./obj --help", "auth", "buckets", "cat", "put")
    run("python3 ./obj cat --help", "--timeout")
    run("python3 ./obj put --help", "--timeout")


def test_obj_cat():
    run("python3 ./obj cat http://lpr-openimages.storage.googleapis.com/openimages-shard.ipynb",
        "with wds.ShardWriter")
