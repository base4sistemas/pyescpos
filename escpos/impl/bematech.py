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
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import time

import six
from six.moves import range

from . import epson
from .. import barcode
from .. import feature
from ..constants import CASHDRAWER_DEFAULT_DURATION
from ..exceptions import CashDrawerException
from ..helpers import _Model

"""
`Bematech S.A. <http://www.bematechus.com/>`_ ESC/POS printer implementation
and ESC/POS derivative command sets.

This manufacturer embed two sets of commands, the default ESC/POS and
another one called *ESC/Bematech* which is based on their own standards,
although looks like some sort of a derivative work.
"""


VENDOR = 'Bematech S/A'


_CASHDRAWER_DURATION_MIN = 50
_CASHDRAWER_DURATION_MAX = 250


class _CommandSet(object):

    def __init__(self, impl):
        super(_CommandSet, self).__init__()
        self._impl = impl

    @property
    def encoding(self):
        return self._impl.encoding

    @property
    def encoding_errors(self):
        return self._impl.encoding_errors


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
        onoff = b'\x31' if flag else b'\x30'
        self._impl.device.write(b'\x1B\x57' + onoff)  # ESC W n

    def set_condensed(self, flag):
        onoff = b'\x0F' if flag else b'\x48'
        self._impl.device.write(b'\x1B' + onoff)

    def set_emphasized(self, flag):
        onoff = b'\x45' if flag else b'\x46'
        self._impl.device.write(b'\x1B' + onoff)

    def _barcode_configure(self, **kwargs):
        if 'barcode_height' in kwargs:
            barcode_height = kwargs.get('barcode_height')
            self._impl.device.write(b'\x1D\x68' + six.int2byte(barcode_height))

        if 'barcode_width' in kwargs:
            widths = {
                    barcode.BARCODE_NORMAL_WIDTH: 2,
                    barcode.BARCODE_DOUBLE_WIDTH: 3,
                    barcode.BARCODE_QUADRUPLE_WIDTH: 4,
                }
            barcode_width = widths.get(kwargs.get('barcode_width'))
            self._impl.device.write(b'\x1D\x77' + six.int2byte(barcode_width))

        if 'barcode_hri' in kwargs:
            values = {
                    barcode.BARCODE_HRI_NONE: 0,
                    barcode.BARCODE_HRI_TOP: 1,
                    barcode.BARCODE_HRI_BOTTOM: 2,
                    barcode.BARCODE_HRI_BOTH: 3,
                }
            barcode_hri = values.get(kwargs.get('barcode_hri'))
            self._impl.device.write(b'\x1D\x48' + six.int2byte(barcode_hri))

    def _barcode_render(self, command):
        self._impl.device.write(command)
        time.sleep(0.25)
        return self._impl.device.read()

    def code128(self, data, **kwargs):
        self._barcode_configure(**kwargs)
        bar_data = data.encode(self.encoding, self.encoding_errors)
        size = six.int2byte(len(bar_data))
        return self._barcode_render(b'\x1D\x6B\x49' + size + bar_data)

    def qrcode(self, data, **kwargs):
        # IMPORTANT WARNING
        #
        # Bematech provides poor documentation for QRCodes [1] in a couple
        # of "developer partners" articles at their web-site, available only in
        # brazilian portuguese, despite its name. These articles does not
        # describe the meaning of 4 parameters.
        #
        # The values used bellow was borrowed from ACBr project [2], where
        # QRCodes are used in receipts for "NFC-e" which is an eletronic legal
        # document.
        #
        # Further illumination was taken from [3].
        #
        # [1] http://partners.bematech.com.br/bemacast/Paginas/post.aspx?idPost=6162
        # [2] http://svn.code.sf.net/p/acbr/code/trunk/Fontes/ACBrNFe2/ACBrNFeDANFeESCPOS.pas
        # [3] http://www.pctoledo.com.br/forum/viewtopic.php?f=20&t=17161
        #
        # Since link [1] isn't a permalink, don't be surprised if it is broken.
        #
        _qr_size_param_0 = 3
        _qr_size_param_1 = 8
        _qr_size_param_2 = 8
        _qr_size_param_3 = 1

        qr_data = data.encode(self.encoding, self.encoding_errors)
        size_H, size_L = divmod(len(qr_data), 256)

        command = (
                b'\x1D\x6B\x51'
                + six.int2byte(_qr_size_param_0)
                + six.int2byte(_qr_size_param_1)
                + six.int2byte(_qr_size_param_2)
                + six.int2byte(_qr_size_param_3)
                + six.int2byte(size_L)
                + six.int2byte(size_H)
                + qr_data
            )

        self._impl.device.write(command)
        time.sleep(1)  # sleeps one second for qrcode to be printed
        response = self._impl.device.read()
        return response

    def kick_drawer(self, port=0, **kwargs):
        # although concrete implementations may have any number of available
        # cash drawer ports, ESC/Bematech foresees two cash drawers anyways
        available_ports = self._impl.hardware_features.get(
                feature.CASHDRAWER_AVAILABLE_PORTS
            )

        if port not in range(available_ports):
            ports_list = ', '.join(str(p) for p in range(available_ports))
            raise CashDrawerException((
                    'invalid cash drawer port: {!r} (hardware features '
                    'only ports: {})'
                ).format(port, ports_list))

        duration = kwargs.get('duration', CASHDRAWER_DEFAULT_DURATION)
        start = _CASHDRAWER_DURATION_MIN
        stop = _CASHDRAWER_DURATION_MAX + 1
        if duration not in range(start, stop):
            raise ValueError((
                    'illegal cash drawer activation duration: {!r} (in '
                    'milliseconds, ranging from {!r} up to {!r}'
                ).format(duration, start, stop))

        if port == 0:
            # activate cash drawer #1 (ESC 76h)
            self._impl.device.write(b'\x1B\x76' + six.int2byte(duration))

        elif port == 1:
            # activate cash drawer #2 (ESC 80h)
            self._impl.device.write(b'\x1B\x80' + six.int2byte(duration))

        else:
            raise CashDrawerException((
                    'invalid cash drawer port: {!r} (ESC/Bematech foresees '
                    'only ports 0 and 1'
                ).format(port))


class MP4200TH(epson.GenericESCPOS):
    """
    Implementation for the Bematech MP-4200 TH POS Printer based on a dual
    command set, ESC/POS and ESC/Bematech, with automatic switching between
    command sets depending on the operation that needs to be performed.
    """

    model = _Model(name='Bematech MP-4200 TH', vendor=VENDOR)

    def __init__(self, device, features={}, **kwargs):
        super(MP4200TH, self).__init__(device, **kwargs)
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
            param = b'\x6D' if partial else b'\x69'
            self.device.write(b'\x1B' + param)

    def _code128_impl(self, data, **kwargs):
        return self._escbema.code128(data, **kwargs)

    def _qrcode_impl(self, data, **kwargs):
        return self._escbema.qrcode(data, **kwargs)

    def _kick_drawer_impl(self, port=0, **kwargs):
        return self._escbema.kick_drawer(port=port, **kwargs)


class MP2800TH(epson.TMT20):
    """Implementation for Bematech MP-2800 TH thermal mini-printer."""

    model = _Model(name='Bematech MP-2800 TH', vendor=VENDOR)

    def __init__(self, device, features={}, **kwargs):
        super(MP2800TH, self).__init__(device, **kwargs)
        self.hardware_features.update({
                feature.CUTTER: True,
                feature.CASHDRAWER_PORTS: True,
                feature.CASHDRAWER_AVAILABLE_PORTS: 1,
                feature.PORTABLE: False,
                feature.COLUMNS: feature.Columns(
                        normal=48,
                        expanded=24,
                        condensed=64
                    ),
            })
        self.hardware_features.update(features)
