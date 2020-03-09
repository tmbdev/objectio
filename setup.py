#!/usr/bin/python3
#
# Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
# This file is part of webloader (see TBD).
# See the LICENSE file for licensing terms (BSD-style).
#

import os
import sys
import setuptools
import datetime

VERSION = open("VERSION", "r").read().strip()

if sys.version_info < (3, 6):
    sys.exit("Python versions less than 3.6 are not supported")

setuptools.setup(
    name='objectio',  # PyPI package name
    version="0.2.29",
    description="Generic object storage interface and commands.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://github.com/tmbdev/objectio",
    author="Thomas Breuel",
    author_email="tmbdev+removeme@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    keywords="object store, client, deep learning",
    packages=["objectio"],
    python_requires=">=3.6",
    scripts=["obj"],
    install_requires="pyyaml braceexpand simplejson typer".split()
)
