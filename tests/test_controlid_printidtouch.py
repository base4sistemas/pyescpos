# -*- coding: utf-8 -*-
#
# escpos/tests/test_controlid_printidtouch.py
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

from escpos.impl.controlid import PrintIdTouch


@pytest.fixture(scope='module')
def printer():
    return PrintIdTouch(pytest.FakeDevice())


def test_has_model_attr(printer):
    assert hasattr(printer, 'model')
