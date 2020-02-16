#
# Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
# This file is part of webloader (see TBD).
# See the LICENSE file for licensing terms (BSD-style).
#
from __future__ import unicode_literals

import os
import sys
import subprocess

def run(script, *args, **kw):
    result = subprocess.check_output(["/bin/bash", "-c", script]).decode("utf-8")
    for arg in args:
        assert arg in result, (arg, result)

def test_obj():
    run("./obj --help", "auth", "buckets", "cat", "put")
    run("./obj cat --help", "--timeout")
    run("./obj put --help", "--timeout")

def test_obj_cat():
    run("./obj cat gs://lpr-openimages/openimages-shard.ipynb",
        "with wds.ShardWriter")
