# -*- coding: utf-8 -*-
#
# escpos/impl/epson.py
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

import re
import time

from .. import barcode
from .. import feature


class GenericESCPOS(object):

    device = None
    """
    The device where ESCPOS commands will be written.

    Indeed, it is an instance of a connection that represents a real device on
    the other end. It may be a serial RS232 connection, a bluetooth connection,
    a USB connection, a network connection, or whatever any other way we can
    ``catch`` it, ``write`` to and ``read`` from.
    """

    hardware_features = {}
    """
    A mapping of hardware features.
    """


    def __init__(self, device, features={}):
        super(GenericESCPOS, self).__init__()
        self.hardware_features = feature._SET
        self.hardware_features.update(features)
        self.device = device
        self.device.catch()


    def init(self):
        self.device.write('\x1B\x40')


    def lf(self, lines=1):
        """
        Line feed. Issues a line feed to printer *n*-times.
        """
        for i in xrange(lines):
            self.device.write('\x0A')


    def textout(self, text):
        """
        Write text "as-is".
        """
        self.device.write(text)


    def text(self, text):
        """
        Write text followed by a line feed.
        """
        self.textout(text)
        self.lf()


    def text_center(self, text):
        """
        Shortcut method for print centered text.
        """
        self.justify_center()
        self.text(text)


    def justify_center(self):
        self.device.write('\x1B\x61\x01')


    def justify_left(self):
        self.device.write('\x1B\x61\x00')


    def justify_right(self):
        self.device.write('\x1B\x61\x02')


    def set_expanded(self, flag):
        raise NotImplementedError()


    def set_condensed(self, flag):
        raise NotImplementedError()


    def set_emphasized(self, flag):
        param = '\x01' if flag else '\x00'
        self.device.write('\x1B\x45' + param)


    def ean13(self, data, **kwargs):
        """
        Render given ``data`` as **EAN-13** barcode symbology.
        """
        if not re.match(r'\d{13}', data):
            raise ValueError('EAN-13 symbology requires 13 digits of data; '
                    'got {:d} digits ("{!s}")'.format(len(data), data))
        barcode.validate_barcode_args(**kwargs)
        return self._ean13_impl(data, **kwargs)


    def _ean13_impl(self, data, **kwargs):
        raise NotImplementedError()


    def ean8(self, data, **kwargs):
        """
        Render given ``data`` as **EAN-8** barcode symbology.
        """
        if not re.match(r'\d{8}', data):
            raise ValueError('EAN-8 symbology requires 8 digits of data; '
                    'got {:d} digits ("{!s}")'.format(len(data), data))
        barcode.validate_barcode_args(**kwargs)
        return self._ean8_impl(data, **kwargs)


    def _ean8_impl(self, data, **kwargs):
        raise NotImplementedError()


    def code128(self, data, **kwargs):
        """
        Render given ``data`` as **Code128** barcode symbology.
        """
        if not re.match(r'^[\x20-\x7F]+$', data):
            raise ValueError('Invalid Code128 symbology. Code128 can encode '
                    'any ASCII character ranging from 32 (20h) to 127 (7Fh); '
                    'got "%s"' % data)
        barcode.validate_barcode_args(**kwargs)
        return self._code128_impl(data, **kwargs)


    def _code128_impl(self, data, **kwargs):
        raise NotImplementedError()


    def qrcode(self, data, **kwargs):
        """
        Render given ``data`` as `QRCode <http://www.qrcode.com/en/>`_.
        """
        barcode.validate_qrcode_args(**kwargs)
        return self._qrcode_impl(data, **kwargs)


    def _qrcode_impl(self, data, **kwargs):
        raise NotImplementedError()


    def cut(self, partial=True):
        """
        Trigger cutter to perform partial (default) or full paper cut.
        """
        if self.hardware_features.get(feature.CUTTER, False):
            # TODO: implement hardware alternative for unavailable features
            # For example:
            #
            #       self.hardware_alternatives.get('cutter-full-cut')(self)
            #
            # So, implementations or end-user-applications can replace
            # certain hardware functionalites, based on available features.
            #
            # The above mapping can replace full cuts with line feeds for
            # printer hardware that do not have an automatic paper cutter:
            #
            #       self.hardware_alternatives.update({
            #               # skip 7 lines if we do not have a paper cutter
            #               'cutter-full-cut': lambda impl: impl.lf(7)
            #           })
            #
            param = '\x01' if partial else '\x00'
            self.device.write('\x1D\x56' + param)


    def kick_drawer(self, port=0, **kwargs):
        """Kick drawer connected to the given port.

        In this implementation, cash drawers are identified according to the
        port in which they are connected. This relation between drawers and
        ports does not exists in the ESC/POS specification and it is just a
        design decision to normalize cash drawers handling. From the user
        application perspective, drawers are simply connected to port 0, 1, 2,
        and so on.

        If printer does not have this feature then nothing happens.

        :param int number: The port number to kick drawer (default is ``0``).

        :raises CashDrawerException: If given port does not exists.
        """
        if self.hardware_features.get(feature.CASHDRAWER_PORTS, False):
            # if feature is available assume at least one port is available
            max_ports = self.hardware_features.get(
                    feature.CASHDRAWER_AVAILABLE_PORTS, 1)

            if port not in xrange(max_ports):
                raise CashDrawerException('invalid cash drawer port: {!r} '
                        '(available ports are {!r})'.format(
                                port, range(max_ports)))

            return self._kick_drawer_impl(port=port, **kwargs)


    def _kick_drawer_impl(self, port=0, **kwargs):
        if port not in xrange(2):
            raise CashDrawerException(
                    'invalid cash drawer port: {!r}'.format(port))

        param = '\x00' if port == 0 else '\x01' # pulse to pin 2 or 5
        self.device.write('\x1B\x70' + param)
