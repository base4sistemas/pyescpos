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

from .. import barcode
from .. import feature
from ..exceptions import CashDrawerException
from ..helpers import is_value_in
from .epson import GenericESCPOS


_CASHDRAWER_DEFAULT_DURATION = 200
"""Duration for cash drawer activation (kick) in milliseconds."""

_CASHDRAWER_DURATION_MIN = 50
_CASHDRAWER_DURATION_MAX = 250


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

    def set_expanded(self, flag):
        onoff = '\x31' if flag else '\x30'
        self._impl.device.write('\x1B\x57' + onoff) # ESC W n


    def set_condensed(self, flag):
        onoff = '\x0F' if flag else '\x48'
        self._impl.device.write('\x1B' + onoff)


    def set_emphasized(self, flag):
        onoff = '\x45' if flag else '\x46'
        self._impl.device.write('\x1B' + onoff)


    def _barcode_configure(self, **kwargs):
        if 'barcode_height' in kwargs:
            barcode_height = kwargs.get('barcode_height')
            self._impl.device.write('\x1D\x68' + chr(barcode_height))

        if 'barcode_width' in kwargs:
            widths = {
                    barcode.BARCODE_NORMAL_WIDTH: 2,
                    barcode.BARCODE_DOUBLE_WIDTH: 3,
                    barcode.BARCODE_QUADRUPLE_WIDTH: 4,}
            barcode_width = widths.get(kwargs.get('barcode_width'))
            self._impl.device.write('\x1D\x77' + chr(barcode_width))

        if 'barcode_hri' in kwargs:
            values = {
                    barcode.BARCODE_HRI_NONE: 0,
                    barcode.BARCODE_HRI_TOP: 1,
                    barcode.BARCODE_HRI_BOTTOM: 2,
                    barcode.BARCODE_HRI_BOTH: 3,}
            barcode_hri = values.get(kwargs.get('barcode_hri'))
            self._impl.device.write('\x1D\x48' + chr(barcode_hri))


    def _barcode_render(self, command):
        self._impl.device.write(command)
        time.sleep(0.25)
        return self._impl.device.read()


    def code128(self, data, **kwargs):
        self._barcode_configure(**kwargs)
        return self._barcode_render(
                '\x1D\x6B\x49{}{}'.format(chr(len(data)), data))


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


    def kick_drawer(self, port=0, **kwargs):
        # although concrete implementations may have any number of available
        # cash drawer ports, ESC/Bematech foresees two cash drawers anyways
        available_ports = self._impl.hardware_features.get(
                feature.CASHDRAWER_AVAILABLE_PORTS)

        if port not in xrange(available_ports):
            ports_list = ', '.join(str(p) for p in xrange(available_ports))
            raise CashDrawerException('invalid cash drawer port: {!r} '
                    '(hardware features only ports: {})'.format(
                            port,
                            ports_list))

        duration = kwargs.get('duration', _CASHDRAWER_DEFAULT_DURATION)
        if duration not in xrange(
                _CASHDRAWER_DURATION_MIN, _CASHDRAWER_DURATION_MAX + 1):
            raise ValueError('illegal cash drawer activation duration: {!r} '
                    '(in milliseconds, ranging from {!r} up to {!r}'.format(
                            duration,
                            _CASHDRAWER_DURATION_MIN,
                            _CASHDRAWER_DURATION_MAX))

        if port == 0:
            # activate cash drawer #1 (ESC 76h)
            self._impl.device.write('\x1B\x76' + chr(duration))

        elif port == 1:
            # activate cash drawer #2 (ESC 80h)
            self._impl.device.write('\x1B\x80' + chr(duration))

        else:
            raise CashDrawerException('invalid cash drawer port: {!r} '
                    '(ESC/Bematech foresees only ports 0 and 1'.format(port))


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
                feature.CASHDRAWER_PORTS: True,
                feature.CASHDRAWER_AVAILABLE_PORTS: 1,
            })
        self.hardware_features.update(features)
        self._escpos = _ESCPOS(self)
        self._escbema = _ESCBematech(self)


    def set_expanded(self, flag):
        self._escbema.set_expanded(flag)


    def set_condensed(self, flag):
        self._escbema.set_condensed(flag)


    def set_emphasized(self, flag):
        self._escbema.set_emphasized(flag)


    def cut(self, partial=True):
        if self.hardware_features.get(feature.CUTTER, False):
            param = '\x6D' if partial else '\x69'
            self.device.write('\x1B' + param)


    def _code128_impl(self, data, **kwargs):
        return self._escbema.code128(data, **kwargs)


    def _qrcode_impl(self, data, **kwargs):
        return self._escbema.qrcode(data, **kwargs)


    def _kick_drawer_impl(self, port=0, **kwargs):
        return self._escbema.kick_drawer(port=port, **kwargs)

