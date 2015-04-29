# -*- coding: utf-8 -*-
#
# escpos/impl/bematech.py
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
    `Bematech S.A. <http://www.bematechus.com/>`_ ESC/POS printer implementation
    and ESC/POS derivative command sets. 

    This manufacturer embed two sets of commands, the default ESC/POS and
    another one called *ESC/Bematech* which is based on their own standards,
    although looks like some sort of a derivative work.
"""

import re
import time

from .. import feature
from ..helpers import is_value_in
from .epson import GenericESCPOS


BARCODE_HRI_NONE = 0
BARCODE_HRI_TOP = 1
BARCODE_HRI_BOTTOM = 2
BARCODE_HRI_BOTH = 3 # should be ignored in future normalization

BARCODE_HRI_POSITIONING = (
        (BARCODE_HRI_NONE, u'No HRI'),
        (BARCODE_HRI_TOP, u'HRI on top of barcode'),
        (BARCODE_HRI_BOTTOM, u'HRI on bottom of barcode'),
        (BARCODE_HRI_BOTH, u'HRI on both top and bottom of bar code'),
    )


BARCODE_NORMAL_WIDTH = 2
BARCODE_DOUBLE_WIDTH = 3
BARCODE_QUADRUPLE_WIDTH = 4 # not sure about this in future normalization

BARCODE_WIDTHS = (
        (BARCODE_NORMAL_WIDTH, u'Normal width'),
        (BARCODE_DOUBLE_WIDTH, u'Double width'),
        (BARCODE_QUADRUPLE_WIDTH, u'Quadruple width'),
    )


BARCODE_HEIGHT_RATIO = 0.125 # mm

BARCODE_HEIGHT_MIN = 2 # mm

BARCODE_HEIGHT_MAX = 31 # mm (255 * 0.125)

DEFAULT_BARCODE_WIDTH = BARCODE_NORMAL_WIDTH

DEFAULT_BARCODE_HEIGHT = 20 # mm (~162 as stated by documentation)

BARCODE_CODE128_PATTERN  = re.compile(r'^[\x20-\x7F]+$')


class _CommandSet(object):

    def __init__(self, impl):
        super(_CommandSet, self).__init__()
        self._impl = impl


class _ESCPOS(_CommandSet):
    """
    Implementation of the ESC/POS standard according to the POS Printer 
    MP-4200 TH Programmer’s Manual, revision 1.0.
    """
    pass


class _ESCBematech(_CommandSet):
    """
    Implementation of the ESC/Bematech standard according to the POS Printer 
    MP-4200 TH Programmer’s Manual, revision 1.0.
    """

    def _configure_barcode(self, **kwargs):
        self._set_barcode_hri(**kwargs)
        self._set_barcode_height(**kwargs)
        self._set_barcode_width(**kwargs)


    def _set_barcode_hri(self, **kwargs):
        hri = kwargs.get('barcode_hri', BARCODE_HRI_TOP)
        if not is_value_in(BARCODE_HRI_POSITIONING, hri):
            raise ValueError('Invalid HRI value: %s' % hri)
        self._impl.device.write('\x1D\x48' + chr(hri))


    def _set_barcode_height(self, **kwargs):
        height = kwargs.get('barcode_height', DEFAULT_BARCODE_HEIGHT)
        if BARCODE_HEIGHT_MIN <= height <= BARCODE_HEIGHT_MAX:
            _height = int(height / BARCODE_HEIGHT_RATIO)
            self._impl.device.write('\x1D\x68' + chr(_height))
        else:
            raise ValueError('Invalid barcode height: %s (mm)' % height)


    def _set_barcode_width(self, **kwargs):
        width = kwargs.get('barcode_width', DEFAULT_BARCODE_WIDTH)
        if not is_value_in(BARCODE_WIDTHS, width):
            raise ValueError('Invalid barcode width: %s' % width)
        self._impl.device.write('\x1D\x77' + chr(width)) # man. pg. 40


    def set_condensed(self, flag):
        onoff = '\x0F' if flag else '\x48'
        self._impl.device.write('\x1B' + onoff)


    def set_emphasized(self, flag):
        onoff = '\x45' if flag else '\x46'
        self._impl.device.write('\x1B' + onoff)


    def code128(self, data, **kwargs): # man. pg. 43
        if not BARCODE_CODE128_PATTERN.match(data):
            raise ValueError('Invalid Code128 symbology.')

        self._configure_barcode(**kwargs)

        code = '\x1D\x6B\x49{}{}'.format(chr(len(data)), data)
        self._impl.device.write(code)
        time.sleep(0.25) # sleeps quarter-second for barcode to be printed
        response = self._impl.device.read()
        return response


    def qrcode(self, data, **kwargs):
        # IMPORTANT WARNING
        # 
        # Bematech provides a poor documentation for QRCodes [1] in a couple
        # of "developer partners" articles at their web-site, available only in
        # brazilian portuguese, despite its name. These articles does not 
        # describe the meaning of 4 parameters.
        #
        # The values used bellow was borrowed from ACBr project [2], where
        # QRCodes are used in receipts for "NFC-e" which is an eletronic legal
        # document.
        #
        # [1] http://partners.bematech.com.br/bemacast/Paginas/post.aspx?idPost=6162
        # [2] http://svn.code.sf.net/p/acbr/code/trunk/Fontes/ACBrNFe2/ACBrNFeDANFeESCPOS.pas
        #
        # Since link [1] isn't a permalink, don't be surprised if it's broken.
        #
        _unknown_param_1 = 3
        _unknown_param_2 = 8
        _unknown_param_3 = 8
        _unknown_param_4 = 1

        size_L = len(data) % 255
        size_H = len(data) / 255

        command = '\x1D\x6B\x51' + \
                chr(_unknown_param_1) + \
                chr(_unknown_param_2) + \
                chr(_unknown_param_3) + \
                chr(_unknown_param_4) + \
                chr(size_L) + \
                chr(size_H) + \
                data
                    
        self._impl.device.write(command)
        time.sleep(1) # sleeps one second for qrcode to be printed
        response = self._impl.device.read()
        return response


class MP4200TH(GenericESCPOS):
    """
    Implementation for the Bematech MP-4200 TH POS Printer based on a dual
    command set, ESC/POS and ESC/Bematech, with automatic switching between
    command sets depending on the operation that needs to be performed.
    """

    def __init__(self, device, features={}):
        super(MP4200TH, self).__init__(device)
        self.hardware_features.update({
                feature.CUTTER: True,
            })
        self.hardware_features.update(features)
        self._escpos = _ESCPOS(self)
        self._escbema = _ESCBematech(self)


    def set_condensed(self, flag):
        self._escbema.set_condensed(flag)


    def set_emphasized(self, flag):
        self._escbema.set_emphasized(flag)


    def code128(self, data, **kwargs):
        return self._escbema.code128(data, **kwargs)


    def qrcode(self, data, **kwargs):
        return self._escbema.qrcode(data, **kwargs)


    def cut(self, partial=True):
        if self.hardware_features.get(feature.CUTTER, False):
            param = '\x6D' if partial else '\x69'
            self.device.write('\x1B' + param)
