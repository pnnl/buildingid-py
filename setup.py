#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pnnl-buildingid: setup.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

from setuptools import setup, find_packages
from codecs import open
from os import path
from zipfile import ZipFile
from io import BytesIO
from requests import get


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

def get_version(relpath):
    with open(path.join(here, relpath), encoding='cp437') as f:
        for line in f:
            if '__version__' in line:
                if '"' in line:
                    return line.split('"')[1]
                elif "'" in line:
                    return line.split("'")[1]
    return None

setup(
    name='pnnl-buildingid',
    version=get_version('buildingid/version.py'),
    description='Unique Building Identifier (UBID)',
    long_description=long_description,
    url='https://github.com/pnnl/buildingid',
    author='Mark Borkum',
    author_email='mark.borkum@pnnl.gov',
    license='BSD-2-Clause',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # keywords=[],

    packages=find_packages(exclude=['bin', 'contrib', 'data', 'docs', 'open-location-code', 'test_data', 'tests*']),

    install_requires=[
        'click',
        'deprecation',
        'pyproj',
        'pyshp',
        'shapely',
    ],

    python_requires='>=3',

    extras_require={
        'dev': [
            'check-manifest',
        ],
        'test': [
            'coverage',
        ],
    },

    entry_points={
        'console_scripts': [
            'buildingid=buildingid.command_line:cli',
        ],
    },
)

# Install open-location-code python module
r = get('https://github.com/google/open-location-code/archive/68ba7ed4c6e7fae41a0255e4394ba1fa0f8435bb.zip')
z = ZipFile(BytesIO(r.content))
z.extract('open-location-code-68ba7ed4c6e7fae41a0255e4394ba1fa0f8435bb/python/openlocationcode.py')
