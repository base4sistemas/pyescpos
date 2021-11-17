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
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time

from . import constants


logger = logging.getLogger('escpos.retry')


def always_retry(e):
    """
    A default exception handler that will always return ``True`` no matter
    what exception ``e`` is.
    """
    return True


def noop(e):
    pass


def backoff(
        max_tries=constants.BACKOFF_DEFAULT_MAXTRIES,
        delay=constants.BACKOFF_DEFAULT_DELAY,
        factor=constants.BACKOFF_DEFAULT_FACTOR,
        exception_handler=always_retry,
        before_delay_handler=noop,
        after_delay_handler=noop):
    """
    Implements an exponential backoff decorator which will retry if the
    exception handler returns ``True``. This implementation is based on
    `Retry <https://wiki.python.org/moin/PythonDecoratorLibrary#Retry>`_ from
    the *Python Decorator Library*.

    :param int max_tries: Number of tries before give up. Defaults to
        :const:`~escpos.constants.BACKOFF_DEFAULT_MAXTRIES`.

    :param int delay: Delay between retries (in seconds). Defaults to
        :const:`~escpos.constants.BACKOFF_DEFAULT_DELAY`.

    :param int factor: Multiply factor in which delay will be increased for
        the next retry. Defaults to
        :const:`~escpos.constants.BACKOFF_DEFAULT_FACTOR`.

    :param exception_handler: Optional callable. Back off algorithm will call
        this handler upon any exception that happens in the decorated function.
        This handler can analyze the exception and decide to retry by returning
        a truthy value or to give up by returning a falsy value. The default
        will :func:`always_retry`, no matter what exception has happened.

    :param before_delay_handler: Optional callable. Back off algorithm will
        call this handler before delaying, when a retry operation is running,
        just after the ``exception_handler`` signaled to retry upon a given
        exception. Any return value will be ignored.

    :param after_delay_handler: Optional callable. Back off algorithm will call
        this handler just after delaying, when a retry operation is running,
        just after the delaying between retries. Any return value will be
        ignored.

    :type exceptions: tuple[Exception]

    """
    if max_tries <= 0:
        raise ValueError((
                'Max tries must be greater than 0; got {!r}'
            ).format(max_tries))

    if delay <= 0:
        raise ValueError((
                'Delay must be greater than 0; got {!r}'
            ).format(delay))

    if factor <= 1:
        raise ValueError((
                'Backoff factor must be greater than 1; got {!r}'
            ).format(factor))

    def outter(f):
        def inner(*args, **kwargs):
            m_max_tries, m_delay = max_tries, delay  # make mutable
            while m_max_tries > 0:
                try:
                    retval = f(*args, **kwargs)
                except Exception as ex:
                    m_max_tries -= 1  # consume an attempt
                    if m_max_tries < 0:
                        # run out of tries
                        raise
                    if exception_handler(ex):
                        logger.info(
                                (
                                    'backoff retry for: %r (max_tries=%r, '
                                    'delay=%r, factor=%r)'
                                ),
                                f,
                                max_tries,
                                delay,
                                factor
                            )
                        before_delay_handler(ex)
                        time.sleep(m_delay)  # wait...
                        after_delay_handler(ex)
                        m_delay *= factor  # make future wait longer
                    else:
                        # exception handler gave up
                        raise
                else:
                    # done without errors
                    return retval
        return inner
    return outter
