# -*- coding: utf-8 -*-
#
# escpos/impl/controlid.py
#
# Copyright 2021 Base4 Sistemas
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

from .. import feature
from ..helpers import _Model
from .epson import TMT20


VENDOR = 'Control iD'


class PrintIdTouch(TMT20):
    """Implementation for Control iD Print iD Touch thermal mini-printer."""

    model = _Model(name='Print iD Touch', vendor=VENDOR)

    def __init__(self, device, features={}, **kwargs):
        super(PrintIdTouch, self).__init__(device, **kwargs)
        self.hardware_features.update({feature.CUTTER: True})
        self.hardware_features.update(features)
