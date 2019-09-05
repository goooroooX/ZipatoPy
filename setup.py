#################################################
#        Setup script for Zipato Python API     #
#            author: Dmitry Nikolaenya          #
#            https://github.com/goooroooX       #
#               https://gooorooo.com            #
#################################################

# Copyright 2019 Dmitry Nikolaenya
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function

import sys

if sys.version_info < (2, 7):
  print('Zipato Python API requires python version >= 2.7.',
        file=sys.stderr)
  sys.exit(1)

from setuptools import setup

packages = [
    'zipatopy',
]

install_requires = []

with open("README.md", "r") as fh:
    long_description = fh.read()

import zipatopy
version = zipatopy.__version__

setup(
    name="zipatopy",
    version=version,
    description="The Python library to interact with Zipato smarthome controllers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dmitry Nikolaenya",
    url="https://github.com/goooroooX/ZipatoPy",
    install_requires=install_requires,
    packages=packages,
    package_data={},
    license="Apache 2.0",
    keywords="zipato api client",
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
