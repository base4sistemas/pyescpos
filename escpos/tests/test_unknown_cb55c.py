# -*- coding: utf-8 -*-
#
# escpos/tests/test_unknown_cb55c.py
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
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from escpos.impl.unknown import CB55C


@pytest.fixture(scope='module')
def printer():
    return CB55C(pytest.FakeDevice())


def test_has_model_attr(printer):
    assert hasattr(printer, 'model')


def test_expanded(printer):
    printer.set_expanded(True)
    assert b'\x1B\x57\x01' == printer.device.write_buffer

    printer.set_expanded(False)
    assert b'\x1B\x57\x00' == printer.device.write_buffer


def test_condensed(printer):
    printer.set_condensed(True)
    assert b'\x1B\x21\x01' == printer.device.write_buffer

    printer.set_condensed(False)
    assert b'\x1B\x21\x00' == printer.device.write_buffer


def test_emphasized(printer):
    printer.set_emphasized(True)
    assert b'\x1B\x45' == printer.device.write_buffer

    printer.set_emphasized(False)
    assert b'\x1B\x46' == printer.device.write_buffer
