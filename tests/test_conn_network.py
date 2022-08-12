# -*- coding: utf-8 -*-
#
# pyescpos/tests/test_conn_network.py
#
# Copyright 2020 Base4 Sistemas EIRELI
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


from pyescpos.conn.network import NetworkConnection


def test_has_settings_example_attribute():
    assert hasattr(NetworkConnection, 'SETTINGS_EXAMPLE')
