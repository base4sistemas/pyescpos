# -*- coding: utf-8 -*-
#
# escpos/config.py
#
# Copyright 2018 Base4 Sistemas Ltda ME
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

from __future__ import absolute_import

import logging
import os

from ConfigParser import SafeConfigParser
from collections import namedtuple

from . import constants


RETRY_SECTION = 'retry'

DEFAULT_CONFIG_FILENAME = os.path.join(os.path.expanduser('~'), '.escpos', 'config.cfg')

RetrySettings = namedtuple('RetrySettings', ['max_tries', 'delay', 'factor',])

retry = None

logger = logging.getLogger('escpos.config')


def configure(filename=None):
    """This function gives to the user application a chance to define where
    configuration file should live. Subsequent calls to this function will have
    no effect, unless you call :func:`reconfigure`.

    :param str filename: Full path to configuration file.

    """
    global retry

    if getattr(configure, '_configured', False):
        return

    filename = filename or DEFAULT_CONFIG_FILENAME
    _ensure_directory(filename)

    parser = SafeConfigParser()

    if os.path.isfile(filename):
        with open(filename, 'r') as fp:
            parser.readfp(fp)

    if not parser.has_section(RETRY_SECTION):
        parser.add_section(RETRY_SECTION)
        parser.set(RETRY_SECTION, 'max_tries', str(constants.BACKOFF_DEFAULT_MAXTRIES))
        parser.set(RETRY_SECTION, 'delay', str(constants.BACKOFF_DEFAULT_DELAY))
        parser.set(RETRY_SECTION, 'factor', str(constants.BACKOFF_DEFAULT_FACTOR))

        with open(filename, 'wb') as fp:
            parser.write(fp)

    retry = RetrySettings(
            max_tries=parser.getint(RETRY_SECTION, 'max_tries'),
            delay=parser.getint(RETRY_SECTION, 'delay'),
            factor=parser.getint(RETRY_SECTION, 'factor'))

    setattr(configure, '_configured', True)
    setattr(configure, '_configured_filename', filename)


def reconfigure(filename=None):
    setattr(configure, '_configured', False)
    configure(filename=filename)


def _ensure_directory(filename):
    path, _ = os.path.split(filename)
    if not os.path.isdir(path):
        logger.warning('creating configuration directory for: %r', filename)
        os.makedirs(path)
