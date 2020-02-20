#!/usr/bin/python3
#
# Copyright (c) 2017-2019 NVIDIA CORPORATION. All rights reserved.
# This file is part of webloader (see TBD).
# See the LICENSE file for licensing terms (BSD-style).
#

import sys
import setuptools

VERSION = '0.1.8'

if sys.version_info < (3, 6):
    sys.exit("Python versions less than 3.6 are not supported")

setuptools.setup(
    name='objio',
    version=VERSION,
    description="Generic object storage interface and commands.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://github.com/tmbdev/objio",
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
    packages=["objio"],
    python_requires=">=3.6",
    scripts=["obj"],
    install_requires="pyyaml braceexpand simplejson typer".split()
)
