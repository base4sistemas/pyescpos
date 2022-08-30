# -*- coding: utf-8 -*-
#
# pyescpos/impl/daruma.py
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

import time

import six

from .. import asc
from .. import barcode
from .. import feature
from ..helpers import _Model
from .epson import GenericESCPOS


"""
`Daruma Urmet <http://www.daruma.com.br/>`_ ESC/POS printer implementation.
"""


VENDOR = 'Urmet Daruma'

_QRCODE_MAX_DATA_SIZE = 700
_QRCODE_ECC_LEVEL_AUTO = 0
_QRCODE_MODULE_SIZE_AUTO = 0

_EAN13_ID = 1
_EAN8_ID = 2
_CODE128_ID = 5


class DarumaGeneric(GenericESCPOS):
    """Base implementation for Urmet Daruma ESC/POS mini-printers."""

    model = _Model(name='Generic Daruma', vendor=VENDOR)

    def __init__(self, device, features={}, **kwargs):
        super(DarumaGeneric, self).__init__(device, **kwargs)
        self.hardware_features.update({
                feature.CUTTER: False,
                feature.CASHDRAWER_PORTS: True,
                feature.CASHDRAWER_AVAILABLE_PORTS: 1,
            })
        self.hardware_features.update(features)

    def justify_center(self):
        self.device.write(b'\x1B\x6A\x01')

    def justify_left(self):
        self.device.write(b'\x1B\x6A\x00')

    def justify_right(self):
        self.device.write(b'\x1B\x6A\x02')

    def set_expanded(self, flag):
        param = b'\x01' if flag else b'\x00'
        self.device.write(b'\x1B\x57' + param)

    def set_condensed(self, flag):
        param = asc.SI if flag else asc.DC2
        self.device.write(six.int2byte(param))

    def set_emphasized(self, flag):
        param = asc.DC1 if flag else asc.DC3
        self.device.write(six.int2byte(param))

    def cut(self, partial=True, feed=0):
        """Trigger cutter to perform full paper cut.

        .. note::

            Daruma ESC/POS command set does not offer control over full or
            partial cut directly through cutter trigger command.

        """
        if self.hardware_features.get(feature.CUTTER, False):
            self.device.write(b'\x1B\x6d')

    def _barcode_impl(self, data, symbology, **kwargs):
        barcode_height = _translate_barcode_height(
                kwargs.get('barcode_height', 50)
            )

        barcode_width = _translate_barcode_width(
                kwargs.get('barcode_width', barcode.BARCODE_NORMAL_WIDTH)
            )

        barcode_hri = _translate_barcode_hri(
                kwargs.get('barcode_hri', barcode.BARCODE_HRI_NONE)
            )

        height = six.int2byte(barcode_height)
        width = six.int2byte(barcode_width)
        hri = six.int2byte(barcode_hri)
        param_symbology = six.int2byte(symbology)
        param_data = data.encode(self.encoding, self.encoding_errors)

        command = (
                b'\x1B\x62'
                + param_symbology
                + width
                + height
                + hri
                + param_data
                + b'\x00'
            )

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
                kwargs.get('qrcode_ecc_level', None)
            ) or _QRCODE_ECC_LEVEL_AUTO

        qrcode_module_size = _translate_qrcode_module_size(
                kwargs.get('qrcode_module_size', None)
            ) or _QRCODE_MODULE_SIZE_AUTO

        qr_data = data.encode(self.encoding, self.encoding_errors)
        data_length = len(qr_data)

        if data_length > _QRCODE_MAX_DATA_SIZE:
            raise ValueError((
                    'too much data: {!r} length (max allowed is {!r})'
                ).format(data_length, _QRCODE_MAX_DATA_SIZE,))

        size_L = data_length >> 8
        size_H = (data_length & 255) + 2

        command = (
                b'\x1B\x81'
                + six.int2byte(size_H)
                + six.int2byte(size_L)
                + six.int2byte(qrcode_module_size)
                + six.int2byte(qrcode_ecc_level)
                + qr_data
            )

        self.device.write(command)

        time.sleep(0.5)
        response = self.device.read()
        return response

    def _kick_drawer_impl(self, port=0, **kwargs):
        self.device.write(b'\x1B\x70')


class DR700(DarumaGeneric):
    """Urmet Daruma DR700 thermal printer implementation.
    Support models DR700 L/H/M and DR700 L-e/H-e.
    """

    model = _Model(name='Daruma DR700', vendor=VENDOR)

    def __init__(self, device, features={}, **kwargs):
        super(DR700, self).__init__(device, **kwargs)
        self.hardware_features.update({
                feature.COLUMNS: feature.Columns(
                        normal=48,
                        expanded=24,
                        condensed=57)
            })
        self.hardware_features.update(features)


class DR800(DarumaGeneric):
    """Urmet Daruma DR800 thermal printer implementation.
    Support models DR800 L and H.
    """

    model = _Model(name='Daruma DR800', vendor=VENDOR)

    def __init__(self, device, features=None, **kwargs):
        super(DR800, self).__init__(device, **kwargs)
        self.hardware_features.update({feature.CUTTER: True})
        self.hardware_features.update(features or {})


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
            barcode.QRCODE_ERROR_CORRECTION_L: 77,  # "L" == "M"
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
            barcode.QRCODE_MODULE_SIZE_8: 7,  # 8 == 7
        }
    return values.get(value, None)
