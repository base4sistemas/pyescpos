# -*- coding: utf-8 -*-
#
# escpos/tests/test_elgin_i9.py
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

import pytest

from escpos.exceptions import CashDrawerException
from escpos.impl.elgin import ElginI9


@pytest.fixture(scope='module')
def printer():
    return ElginI9(pytest.FakeDevice())


def test_has_model_attr(printer):
    assert hasattr(printer, 'model')


def test_kick_drawer(printer):
    printer.kick_drawer()
    assert printer.device.write_buffer == '\x1B\x70\x00\x20\xe8'


def test_kick_drawer_unavailable_port(printer):
    with pytest.raises(CashDrawerException):
        # Elgin I9 has only one cash drawer port
        printer.kick_drawer(port=1)


def test_kick_drawer_custom_pulse_duration(printer):
    printer.kick_drawer(duration=100) # 100ms (resulting t1='\x20', t2='\x84')
    assert printer.device.write_buffer == '\x1B\x70\x00\x20\x84'


def test_kick_drawer_custom_pulse_duration_explicit_interval(printer):
    printer.kick_drawer(t1='\x64', t2='\xC8') # t1=100ms, t2=200ms
    assert printer.device.write_buffer == '\x1B\x70\x00\x64\xC8'
