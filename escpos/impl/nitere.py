# -*- coding: utf-8 -*-
#
# escpos/impl/nitere.py
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

from ..helpers import _Model
from .unknown import CB55C


_VENDOR = u'Nitere'


class NitereNPDV1020(CB55C):
    """Alias for **Unknown OEM** :class:`~escpos.impl.unknown.CB55C` model."""

    model = _Model(name=u'Nitere NPDV-1020', vendor=_VENDOR)


    def __init__(self, device, features={}):
        super(NitereNPDV1020, self).__init__(device, features=features)
