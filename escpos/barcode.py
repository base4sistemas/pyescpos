# -*- coding: utf-8 -*-
#
# escpos/barcode.py
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

import re


DEFAULT_BARCODE_WIDTH = 2

DEFAULT_BARCODE_HEIGHT = 50


class Barcode(object):

    def __init__(self, data,
            bar_width=DEFAULT_BARCODE_WIDTH,
            bar_height=DEFAULT_BARCODE_HEIGHT,
            labeled=True):

        super(Barcode, self).__init__()
        self.data = data
        self.symbology = None
        self.bar_width = bar_width
        self.bar_height = bar_height
        self.labeled = labeled


    def render(self):
        if self.symbology is None:
            raise ValueError('Unknown barcode symbology')
        labeled = '\x01' if self.labeled else '\x00'
        code = '\x1B\x62{symbology}{barw}{barh}{labeled}{data}\x00'.format(
                symbology=chr(self.symbology),
                barw=chr(self.bar_width),
                barh=chr(self.bar_height),
                labeled=labeled,
                data=self._get_data_for_rendering())
        return code


    def _get_data_for_rendering(self):
        return self.data



class BarcodeEAN13(Barcode):

    EAN13_PATTERN = re.compile(r'\d{13}')

    def __init__(self, data, **kwargs):
        super(BarcodeEAN13, self).__init__(data, **kwargs)
        self.symbology = 1

        if not self.EAN13_PATTERN.match(data):
            raise ValueError('EAN-13 symbology requires 13 digits of data; '
                    'got %d digits ("%s")' % (len(data), data,))
        

    def _get_data_for_rendering(self):
        # truncate to 12 digits, since check-digit will be
        # calculated by device firmware...
        return self.data[:12]


class BarcodeEAN8(Barcode):

    EAN8_PATTERN = re.compile(r'\d{8}')

    def __init__(self, data, **kwargs):
        super(BarcodeEAN8, self).__init__(data, **kwargs)
        self.symbology = 2

        if not self.EAN8_PATTERN.match(data):
            raise ValueError('EAN-8 symbology requires 8 digits of data; '
                    'got %d digits ("%s")' % (len(data), data,))


    def _get_data_for_rendering(self):
        # truncate to 7 digits, since check-digit will be
        # calculated by device firmware...
        return self.data[:7]


class BarcodeCode128(Barcode):

    CODE128_PATTERN = re.compile(r'^[\x20-\x7F]+$')

    def __init__(self, data, **kwargs):
        super(BarcodeCode128, self).__init__(data, **kwargs)
        self.symbology = 5
        
        if not self.CODE128_PATTERN.match(data):
            raise ValueError('Invalid Code128 symbology. Code128 can encode '
                    'any ASCII character ranging from 32 (20h) to 127 (7Fh); '
                    'got "%s"' % data)



class QRCode(object):

    def render(self):
        pass


class ImageBasedQRCode(object):

    def render(self):
        pass
        