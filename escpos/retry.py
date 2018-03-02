# -*- coding: utf-8 -*-
#
# escpos/retry.py
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
import time

from . import constants


logger = logging.getLogger('escpos.retry')


def backoff(
        max_tries=constants.BACKOFF_DEFAULT_MAXTRIES,
        delay=constants.BACKOFF_DEFAULT_DELAY,
        factor=constants.BACKOFF_DEFAULT_FACTOR,
        exceptions=None):
    """Implements an exponential backoff decorator which will retry decorated
    function upon given exceptions. This implementation is based on
    `Retry <https://wiki.python.org/moin/PythonDecoratorLibrary#Retry>`_ from
    the *Python Decorator Library*.

    :param int max_tries: Number of tries before give up. Defaults to
        :const:`~escpos.constants.BACKOFF_DEFAULT_MAXTRIES`.

    :param int delay: Delay between retries (in seconds). Defaults to
        :const:`~escpos.constants.BACKOFF_DEFAULT_DELAY`.

    :param int factor: Multiply factor in which delay will be increased for the
        next retry. Defaults to :const:`~escpos.constants.BACKOFF_DEFAULT_FACTOR`.

    :param exceptions: Tuple of exception types to catch that triggers retry.
        Any exception not listed will break the decorator and retry routines
        will not run.

    :type exceptions: tuple[Exception]

    """
    if max_tries <= 0:
        raise ValueError('Max tries must be greater than 0; got {!r}'.format(max_tries))

    if delay <= 0:
        raise ValueError('Delay must be greater than 0; got {!r}'.format(delay))

    if factor <= 1:
        raise ValueError('Backoff factor must be greater than 1; got {!r}'.format(factor))

    def outter(f):
        def inner(*args, **kwargs):
            m_max_tries, m_delay = max_tries, delay # make mutable
            while m_max_tries > 0:
                try:
                    retval = f(*args, **kwargs)
                except exceptions:
                    logger.exception('backoff retry for: %r (max_tries=%r, delay=%r, '
                            'factor=%r, exceptions=%r)', f, max_tries, delay, factor, exceptions)
                    m_max_tries -= 1 # consume an attempt
                    if m_max_tries <= 0:
                        raise # run out of tries
                    time.sleep(m_delay) # wait...
                    m_delay *= factor # make future wait longer
                else:
                    # we're done without errors
                    return retval
        return inner
    return outter
