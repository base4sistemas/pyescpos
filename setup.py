# -*- coding: utf-8 -*-
#
# Copyright 2015 Base4 Sistemas Ltda ME
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
#

import io
import os
import re
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


def read_install_requires():
    content = read(os.path.join('requirements', 'base.txt'))
    return content.strip().split(os.linesep)


def read_version():
    content = read(os.path.join('escpos', '__init__.py'))
    return re.search(r"__version__ = '([^']+)'", content).group(1)


long_description = read('README.rst')


class PyTest(TestCommand):
    # Based on sugested implementation:
    # https://docs.pytest.org/en/latest/goodpractices.html#manual-integration
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import pytest # import here, cause outside the eggs aren't loaded
        import shlex
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

    def run(self):
        # Avoid installing dependencies in a ".egg/" directory during tests
        # execution, which is useful if you are running in a virtualenv and
        # want to use dependencies already installed in your environment.
        self.distribution.install_requires = []
        TestCommand.run(self)


setup(
        name='PyESCPOS',
        version=read_version(),
        description='Support for Epson ESC/POS printer command system.',
        long_description=long_description,
        packages=[
                'escpos',
                'escpos.impl',
                'escpos.conn',
            ],
        install_requires=read_install_requires(),
        tests_require=[
                'pytest',
                'pytest-cov',
            ],
        cmdclass={'test': PyTest},
        include_package_data=True,
        license='Apache Software License',
        platforms='any',
        url='http://github.com/base4sistemas/pyescpos/',
        author='Daniel Gonçalves',
        author_email='daniel@base4.com.br',
        classifiers = [
                'Development Status :: 4 - Beta',
                'Environment :: Other Environment',
                'Intended Audience :: Developers',
                'Intended Audience :: Information Technology',
                'License :: OSI Approved :: Apache Software License',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.7',
                'Topic :: Printing',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Topic :: Office/Business :: Financial :: Point-Of-Sale',
            ]
    )
