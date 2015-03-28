# -*- coding: utf-8 -*-
#
# escpos/tests/test_helpers.py
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

import time
import pytest

from ..helpers import *


def test_chunk():
    data = 'ABCDEFG'
    chunk_size = 3
    for chunk in chunks(data, chunk_size):
        assert len(chunk) <= chunk_size, 'Unexpected chunk size (expecting '\
                'chunks of 3 or less elements)'


def test_timeout():
    timeout = TimeoutHelper(timeout=0.5)
    timeout.set()
    with pytest.raises(TimeoutException):
        time.sleep(1)
        timeout.check()