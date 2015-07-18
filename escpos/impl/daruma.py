# -*- coding: utf-8 -*-
#
# escpos/impl/daruma.py
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
    `Daruma Urmet <http://www.daruma.com.br/>`_ ESC/POS printer implementation.
"""

import time

from .. import asc
from .. import barcode
from .. import feature
from .epson import GenericESCPOS


_QRCODE_MAX_DATA_SIZE = 700
_QRCODE_ECC_LEVEL_AUTO = 0
_QRCODE_MODULE_SIZE_AUTO = 0


_EAN13_ID = 1
_EAN8_ID = 2
_CODE128_ID = 5


class DarumaGeneric(GenericESCPOS):
    """
    Base implementation for Urmet Daruma ESC/POS mini-printers.
    """

    def __init__(self, device, features={}):
        super(DarumaGeneric, self).__init__(device)
        self.hardware_features.update({
                feature.CUTTER: False,
                feature.CASHDRAWER_PORTS: True,
                feature.CASHDRAWER_AVAILABLE_PORTS: 1,
            })
        self.hardware_features.update(features)


    def justify_center(self):
        self.device.write('\x1B\x6A\x01')


    def justify_left(self):
        self.device.write('\x1B\x6A\x00')


    def justify_right(self):
        self.device.write('\x1B\x6A\x02')


    def set_expanded(self, flag):
        param = '\x01' if flag else '\x00'
        self.device.write('\x1B\x57' + param)


    def set_condensed(self, flag):
        self.device.write(chr(asc.SI) if flag else chr(asc.DC2))


    def set_emphasized(self, flag):
        self.device.write(chr(asc.DC1) if flag else chr(asc.DC3))


    def _barcode_impl(self, processed_data, symbology, **kwargs):
        barcode_height = _translate_barcode_height(
                kwargs.get('barcode_height', 50))

        barcode_width = _translate_barcode_width(
                kwargs.get('barcode_width', barcode.BARCODE_NORMAL_WIDTH))

        barcode_hri = _translate_barcode_hri(
                kwargs.get('barcode_hri', barcode.BARCODE_HRI_NONE))

        command = '\x1B\x62{}{}{}{}{}\x00'.format(
                chr(symbology),
                chr(barcode_width),
                chr(barcode_height),
                chr(barcode_hri),
                processed_data)

        self.device.write(command)
        time.sleep(0.25)
        response = self.device.read()
        return response


    def _ean13_impl(self, data, **kwargs):
        return self._barcode_impl(data[:12], _EAN13_ID, **kwargs)


    def _ean8_impl(self, data, **kwargs):
        return self._barcode_impl(data[:7], _EAN8_ID, **kwargs)


    def _code128_impl(self, data, **kwargs):
        return self._barcode_impl(data, _CODE128_ID, **kwargs)


    def _qrcode_impl(self, data, **kwargs):

        qrcode_ecc_level = _translate_qrcode_ecc_level(
                kwargs.get('qrcode_ecc_level', None)) or _QRCODE_ECC_LEVEL_AUTO

        qrcode_module_size = _translate_qrcode_module_size(
                kwargs.get('qrcode_module_size', None)) or \
                        _QRCODE_MODULE_SIZE_AUTO

        data_length = len(data)

        if data_length > _QRCODE_MAX_DATA_SIZE:
            raise ValueError('Too much data: %d length (max allowed is %d)' % (
                    data_length, _QRCODE_MAX_DATA_SIZE,))

        size_L = data_length >> 8
        size_H = (data_length & 255) + 2

        command = '\x1B\x81' + \
                chr(size_H) + chr(size_L) + \
                chr(qrcode_module_size) + \
                chr(qrcode_ecc_level) + \
                data

        self.device.write(command)
        time.sleep(0.5)
        response = self.device.read()
        return response


    def _kick_drawer_impl(self, port=0, **kwargs):
        self.device.write('\x1B\x70')


class DR700(DarumaGeneric):
    """
    Urmet Daruma DR700 thermal printer implementation.
    Support models DR700 L/H/M and DR700 L-e/H-e.
    """
    pass


def _translate_barcode_height(value):
    return 50 if value < 50 else value


def _translate_barcode_width(value):
    values = {
            barcode.BARCODE_NORMAL_WIDTH: 2,
            barcode.BARCODE_DOUBLE_WIDTH: 3,
            barcode.BARCODE_QUADRUPLE_WIDTH: 5,
        }
    return values.get(value)


def _translate_barcode_hri(value):
    values = {
            barcode.BARCODE_HRI_NONE: 0,
            barcode.BARCODE_HRI_TOP: 0,
            barcode.BARCODE_HRI_BOTTOM: 1,
            barcode.BARCODE_HRI_BOTH: 0,
        }
    return values.get(value)


def _translate_qrcode_ecc_level(value):
    values = {
            barcode.QRCODE_ERROR_CORRECTION_L: 77, # "L" == "M"
            barcode.QRCODE_ERROR_CORRECTION_M: 77,
            barcode.QRCODE_ERROR_CORRECTION_Q: 81,
            barcode.QRCODE_ERROR_CORRECTION_H: 72
        }
    return values.get(value, None)


def _translate_qrcode_module_size(value):
    values = {
            barcode.QRCODE_MODULE_SIZE_4: 4,
            barcode.QRCODE_MODULE_SIZE_5: 5,
            barcode.QRCODE_MODULE_SIZE_6: 6,
            barcode.QRCODE_MODULE_SIZE_7: 7,
            barcode.QRCODE_MODULE_SIZE_8: 7, # 8 == 7
        }
    return values.get(value, None)
