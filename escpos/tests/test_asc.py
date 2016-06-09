# -*- coding: utf-8 -*-
#
# escpos/tests/test_asc.py
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

from escpos import asc


def test_mnemonic():
    assert asc.mnemonic(-1) is None, 'There is no mnemonic for ASCII code -1'
    assert asc.mnemonic(32) is None, 'There is no mnemonic for ASCII code 32'
    assert asc.mnemonic(0) == 'NUL', 'Mnemonic for ASCII code 0 should be "NUL"'
    assert asc.mnemonic(31) == 'US', 'Mnemonic for ASCII code 0 should be "US"'


def test_ascii_code_from_mnemonic():
    assert asc.value('ESC') == 27, 'Mnemonic "ESC" should be ASCII code 27'
    assert asc.value('Esc') == 27, 'Mnemonic "Esc" should be ASCII code 27'
    assert asc.value('esc') == 27, 'Mnemonic "esc" should be ASCII code 27'

    with pytest.raises(ValueError):
        asc.value('NOP')
