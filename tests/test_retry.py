# -*- coding: utf-8 -*-
#
# escpos/tests/test_retry.py
#
# Copyright 2021 Base4 Sistemas EIRELI
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

from six.moves import range

import pytest

from escpos.retry import time as time_module
from escpos.retry import backoff


def test_backoff_no_exceptions_raised():
    """Test when decorated function just works."""
    @backoff()
    def decorated():
        return 'OK'
    assert 'OK' == decorated()


def test_backoff_maxtries_arg_validation():
    """The ``max_tries`` argument must be an integer greather than zero."""
    @backoff(max_tries=1)
    def decorated():
        return 'OK'
    assert 'OK' == decorated()

    with pytest.raises(ValueError):
        @backoff(max_tries=0)
        def decorated():
            pass
        decorated()

    for max_tries in range(0, -2, -1):
        with pytest.raises(ValueError):
            @backoff(max_tries=max_tries)
            def decorated():
                pass
            decorated()


def test_backoff_delay_arg_validation():
    """The ``delay`` argument must be an integer greather than zero."""
    @backoff(delay=1)
    def decorated():
        return 'OK'
    assert 'OK' == decorated()

    for delay in range(0, -2, -1):
        with pytest.raises(ValueError):
            @backoff(delay=delay)
            def decorated():
                pass
            decorated()


def test_backoff_factor_arg_validation():
    """The ``factor`` argument must be an integer greather than one."""
    @backoff(factor=2)
    def decorated():
        return 'OK'
    assert 'OK' == decorated()

    for factor in range(1, -2, -1):
        with pytest.raises(ValueError):
            @backoff(factor=factor)
            def decorated():
                pass
            decorated()


def test_backoff_fail_twice_then_succeed(monkeypatch):
    """Decorated function will fail twice and then succeed."""

    # mock time.sleep so we do not have to wait
    monkeypatch.setattr(time_module, 'sleep', lambda seconds: None)

    # NOTE: In Python 2 we cannot use a plain integer variable in inner
    # scope at handler. As of Python 3 the 'nonlocal' keyword will do
    # the trick. See: https://www.python.org/dev/peps/pep-3104/
    counters = {
            'ValueError': 0,
            'before': 0,
            'after': 0,
        }

    def handler(ex):
        counters['ValueError'] += 1
        return True

    def before_delay(ex):
        counters['before'] += 1

    def after_delay(ex):
        counters['after'] += 1

    @backoff(
            max_tries=3,
            delay=1,
            factor=2,
            exception_handler=handler,
            before_delay_handler=before_delay,
            after_delay_handler=after_delay)
    def decorated():
        if counters['ValueError'] < 2:
            raise ValueError()
        return 'OK'

    assert 'OK' == decorated()
    assert counters['ValueError'] == 2
    assert counters['before'] == 2
    assert counters['after'] == 2
