# -*- coding: utf-8 -*-
#
# escpos/impl/unknown.py
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

from .. import feature
from ..helpers import _Model
from .epson import GenericESCPOS


VENDOR = 'Unknown OEM'


class CB55C(GenericESCPOS):
    """Model CB55-C (unknown OEM) thermal receipt printer.

    .. note::

        Implementation based on a CB55-C embedded in Nitere NPDV-1020 model
        TMF-101/IG by Nitere Indústria de Produtos Eletrônicos Ltda EPP.

    .. note::

        When there is **NO** cash drawer connected, the command that follows
        method :meth:`~escpos.impl.epson.GenericESCPOS.kick_drawer` will likely
        fail.

    """

    model = _Model(name='CB55-C', vendor=VENDOR)

    def __init__(self, device, features={}, **kwargs):
        super(CB55C, self).__init__(device, **kwargs)
        self.hardware_features.update({
                feature.CUTTER: True,
                feature.CASHDRAWER_PORTS: True,
                feature.CASHDRAWER_AVAILABLE_PORTS: 1,
            })
        self.hardware_features.update(features)

    def set_expanded(self, flag):
        # ESC W m : double width mode
        param = b'\x01' if flag else b'\x00'  # <m> 0=disable; 1=enable
        self.device.write(b'\x1B\x57' + param)

    def set_condensed(self, flag):
        # ESC ! n : formatting characters
        param = b'\x01' if flag else b'\x00'  # <n> 0=disable; 1=enable (bit 0)
        self.device.write(b'\x1B\x21' + param)

    def set_emphasized(self, flag):
        # ESC E : Enable emphasized mode
        # ESC F : Disable emphasized mode
        param = b'\x45' if flag else b'\x46'
        self.device.write(b'\x1B' + param)
