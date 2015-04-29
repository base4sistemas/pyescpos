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

from __future__ import absolute_import

import time

from .. import asc
from .. import feature
from .epson import GenericESCPOS
from ..helpers import is_value_in


QRCODE_MAX_DATA_SIZE = 700


QRCODE_MODULE_SIZE_AUTO = 0
QRCODE_MODULE_SIZE_4 = 4
QRCODE_MODULE_SIZE_5 = 5
QRCODE_MODULE_SIZE_6 = 6
QRCODE_MODULE_SIZE_7 = 7

QRCODE_MODULE_SIZES = (
        (QRCODE_MODULE_SIZE_AUTO, 'Automatic'),
        (QRCODE_MODULE_SIZE_4, '4'),
        (QRCODE_MODULE_SIZE_5, '5'),
        (QRCODE_MODULE_SIZE_6, '6'),
        (QRCODE_MODULE_SIZE_7, '7'),)


QRCODE_ERROR_CORRECTION_AUTO = 0
QRCODE_ERROR_CORRECTION_M = 77
QRCODE_ERROR_CORRECTION_Q = 81
QRCODE_ERROR_CORRECTION_H = 72

QRCODE_ERROR_CORRECTION_LEVELS = (
        (QRCODE_ERROR_CORRECTION_AUTO, 'Automatic'),
        (QRCODE_ERROR_CORRECTION_M, 'Level M'),
        (QRCODE_ERROR_CORRECTION_Q, 'Level Q'),
        (QRCODE_ERROR_CORRECTION_H, 'Level H'),)


class DarumaGeneric(GenericESCPOS):
    """
    Base implementation for Urmet Daruma ESC/POS printers. Known to work
    on (or tested with) the following models/firmwares:

    * Daruma DR700 L/H/M firmware 02.51.00
    * Daruma DR700 L-e/H-e firmware 01.20.00
    * Daruma DR700 L-e/H-e firmware 01.21.00

    You can checkout `Urmet Daruma <http://www.daruma.com.br/>`_ web site for
    other printer models (web site in brazillian portuguese only).
    """

    def __init__(self, device, features={}):
        super(DarumaGeneric, self).__init__(device)
        self.hardware_features.update({
                feature.CUTTER: False,
            })
        self.hardware_features.update(features)


    def justify_center(self):
        self.device.write('\x1B\x6A\x01')


    def justify_left(self):
        self.device.write('\x1B\x6A\x00')


    def justify_right(self):
        self.device.write('\x1B\x6A\x02')


    def set_expanded(self, flag):
        cmd = '\x1B\x57' + '\x01' if flag else '\x00'
        self.device.write(cmd)


    def set_condensed(self, flag):
        self.device.write(chr(asc.SI) if flag else chr(asc.DC2))


    def set_emphasized(self, flag):
        self.device.write(chr(asc.DC1) if flag else chr(asc.DC3))


    def qrcode(self, data, 
            module_size=QRCODE_MODULE_SIZE_AUTO,
            error_correction_level=QRCODE_ERROR_CORRECTION_AUTO):
        """
        Print QRCode symbol for the given **unicode** data.

        This method is capable of rendering QRCode for Daruma mini-printer
        models DR700 L, DR700 M and DR700 H, from firmware version 02.50.00.
        This code is also tested with the DR700 L-e/H-e firmware 01.21.00.
        """

        if not is_value_in(QRCODE_MODULE_SIZES, module_size):
            raise ValueError('Unexpected module size: %s' % module_size)

        if not is_value_in(QRCODE_ERROR_CORRECTION_LEVELS, 
                error_correction_level):
            raise ValueError('Unexpected error correction level: %s' % \
                    error_correction_level)

        data_length = len(data)

        if data_length > QRCODE_MAX_DATA_SIZE:
            raise ValueError('Too much data: %d length (max allowed is %d)' % (
                    data_length, QRCODE_MAX_DATA_SIZE,))

        size_L = data_length >> 8
        size_H = (data_length & 255) + 2

        command = '\x1B\x81' + \
                chr(size_H) + chr(size_L) + \
                chr(module_size) + \
                chr(error_correction_level) + \
                data

        self.device.write(command)
        time.sleep(1) # sleeps one second for qrcode to be printed
        response = self.device.read()
        return response