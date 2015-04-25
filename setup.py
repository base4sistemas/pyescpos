# -*- coding: utf-8 -*-
# 
# setup.py
#
# This setup script is based on Jeff Knupp's article "Open Sourcing a
# Python Project the Right Way" which can be found at:
# http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
# 

from setuptools import setup
from setuptools.command.test import test as TestCommand
import io
import sys

import escpos


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


long_description = read('README.rst', 'CHANGES.rst')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='PyESCPOS',
    version=escpos.__version__,
    url='http://github.com/base4sistemas/pyescpos/',
    license='Apache Software License',
    author='Daniel Gonçalves',
    tests_require=['pytest'],
    install_requires=[],
    cmdclass={
            'test': PyTest
        },
    author_email='daniel@base4.com.br',
    description='Support for Epson ESC/POS printer command system.',
    long_description=long_description,
    packages=['escpos', 'escpos.impl'],
    include_package_data=True,
    platforms='any',
    test_suite='escpos.tests',
    classifiers = [
            'Development Status :: 1 - Planning',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Printing',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    extras_require={
            'testing': ['pytest'],
        }
    )
