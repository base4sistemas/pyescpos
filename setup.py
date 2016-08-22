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
    content = read('requirements.txt')
    return content.strip().split(os.linesep)


def read_version():
    content = read(os.path.join(
            os.path.dirname(__file__), 'escpos', '__init__.py'))
    return re.search(r"__version__ = '([^']+)'", content).group(1)


long_description = read('README.rst')


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest # import here, cause outside the eggs aren't loaded
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
        name='PyESCPOS',
        version=read_version(),
        description='Support for Epson ESC/POS printer command system.',
        long_description=long_description,
        packages=[
                'escpos',
                'escpos.impl'
            ],
        install_requires=read_install_requires(),
        extras_require={
                'testing': [
                        'pytest',
                        'pytest-cov',
                    ],
            },
        tests_require=['pytest'],
        cmdclass={'test': PyTest},
        test_suite='escpos.tests',
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
                'Topic :: Printing',
                'Topic :: Software Development :: Libraries :: Python Modules',
            ]
    )
