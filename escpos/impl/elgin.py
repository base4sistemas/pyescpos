# -*- coding: utf-8 -*-
#
# escpos/impl/elgin.py
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

"""
    `Elgin <http://www.elgin.com.br/>`_ ESC/POS printer implementation.
"""

from .. import barcode
from .. import feature
from .epson import GenericESCPOS


class ElginGeneric(GenericESCPOS):
    """
    Base implementation for Elgin ESC/POS mini-printers.
    """

    def __init__(self, device, features={}):
        super(ElginGeneric, self).__init__(device)
        self.hardware_features.update({
                feature.CUTTER: False,
                feature.CASHDRAWER_PORTS: True,
                feature.CASHDRAWER_AVAILABLE_PORTS: 1,
            })
        self.hardware_features.update(features)



class ElginI9(ElginGeneric):
    """
    Implementation for Elgin i9 thermal mini-printer.
    """

    def __init__(self, device, features={}):
        super(ElginI9, self).__init__(device)
        self.hardware_features.update({feature.CUTTER: True})
        self.hardware_features.update(features)


    def set_expanded(self, flag):
        w = 1 if flag else 0 # magnification (Nx)
        self.set_text_size(w, 0)


    def set_condensed(self, flag):
        # 00h = character font A (12x24, normal)
        # 01h = character font B (9x17, condensed)
        param = '\x01' if flag else '\x00'
        self.device.write('\x1B\x4D' + param)

