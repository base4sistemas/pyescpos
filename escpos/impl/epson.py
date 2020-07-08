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
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re
import time

import six
from six.moves import range

from .. import barcode
from .. import constants
from .. import feature
from ..exceptions import CashDrawerException
from ..helpers import ByteValue
from ..helpers import is_value_in
from ..helpers import _Model


VENDOR = 'Seiko-Epson Corporation'

FONT_A = b'\x00'
FONT_B = b'\x01'
FONT_C = b'\x02'
FONT_D = b'\x03'
FONT_E = b'\x04'
FONT_SPECIAL_A = b'\x61'
FONT_SPECIAL_B = b'\x62'

AVAILABLE_FONTS = (
        (FONT_A, 'Font A'),
        (FONT_B, 'Font B'),
        (FONT_C, 'Font C'),
        (FONT_D, 'Font D'),
        (FONT_E, 'Font E'),
        (FONT_SPECIAL_A, 'Special Font A'),
        (FONT_SPECIAL_B, 'Special Font B'),
    )

QRCODE_ERROR_CORRECTION_MAP = {
        barcode.QRCODE_ERROR_CORRECTION_L: b'\x30',  # 48d (~7%, default)
        barcode.QRCODE_ERROR_CORRECTION_M: b'\x31',  # 49d (~15%)
        barcode.QRCODE_ERROR_CORRECTION_Q: b'\x32',  # 50d (~25%)
        barcode.QRCODE_ERROR_CORRECTION_H: b'\x33',  # 51d (~30%)
    }


QRCODE_MODULE_SIZE_MAP = {
        barcode.QRCODE_MODULE_SIZE_4: b'\x04',
        barcode.QRCODE_MODULE_SIZE_5: b'\x05',
        barcode.QRCODE_MODULE_SIZE_6: b'\x06',
        barcode.QRCODE_MODULE_SIZE_7: b'\x07',
        barcode.QRCODE_MODULE_SIZE_8: b'\x08',
    }


class GenericESCPOS(object):
    """The ESC/POS base class implementation.

    .. todo::
        Provide default 'GS k' symbology: UPC-A.

    .. todo::
        Provide default 'GS k' symbology: UPC-E.

    .. todo::
        Provide default 'GS k' symbology: Code 39.

    .. todo::
        Provide default 'GS k' symbology: ITF-14.

    .. todo::
        Provide default 'GS k' symbology: Codabar NW-7.

    .. todo::
        Provide default 'GS k' symbology: Code 93.

    .. todo::
        Provide default 'GS k' symbology: GS1-128 (UCC/EAN-128).

    .. todo::
        Provide default 'GS k' symbology: GS1 DataBar Omnidirectional.

    .. todo::
        Provide default 'GS k' symbology: GS1 DataBar Truncated.

    .. todo::
        Provide default 'GS k' symbology: GS1 DataBar Limited.

    .. todo::
        Provide default 'GS k' symbology: GS1 DataBar Expanded.

    """

    device = None
    """The device where ESCPOS commands will be written.

    Indeed, it is an instance of a connection that represents a real device on
    the other end. It may be a serial RS232 connection, a bluetooth connection,
    a USB connection, a network connection, or whatever any other way we can
    ``catch`` it, ``write`` to and ``read`` from.
    """

    hardware_features = None
    """A mapping of hardware features."""

    model = _Model(name='Generic ESC/POS', vendor=VENDOR)
    """Basic metadata with vendor and model name."""

    encoding = constants.DEFAULT_ENCODING
    """Default encoding used to encode data before sending to device."""

    encoding_errors = constants.DEFAULT_ENCODING_ERRORS
    """How to deal with ``UnicodeEncodingError``.
    See ``errors`` argument to ``str.encode()`` for details.
    """

    def __init__(
            self,
            device,
            features=None,
            encoding=constants.DEFAULT_ENCODING,
            encoding_errors=constants.DEFAULT_ENCODING_ERRORS):
        super(GenericESCPOS, self).__init__()
        self._feature_attrs = feature.FeatureAttributes(self)
        self.hardware_features = feature._SET.copy()
        self.hardware_features.update(features or {})
        self.encoding = encoding
        self.encoding_errors = encoding_errors
        self.device = device
        self.device.catch()

    @property
    def feature(self):
        return self._feature_attrs

    def init(self):
        self.device.write(b'\x1B\x40')

    def lf(self, lines=1):
        """Line feed. Issues a line feed to printer *n*-times."""
        for i in range(lines):
            self.device.write(b'\x0A')

    def textout(self, text):
        """Write text without line feed."""
        self.device.write(text.encode(self.encoding, self.encoding_errors))

    def text(self, text):
        """Write text followed by a line feed."""
        self.textout(text)
        self.lf()

    def text_center(self, text):
        """Shortcut method for print centered text."""
        self.justify_center()
        self.text(text)

    def justify_center(self):
        self.device.write(b'\x1B\x61\x01')

    def justify_left(self):
        self.device.write(b'\x1B\x61\x00')

    def justify_right(self):
        self.device.write(b'\x1B\x61\x02')

    def set_code_page(self, code_page):
        """Set code page for character printing.

        Default code page values are described on page 8 from Epson's
        `FAQ about ESC/POS <http://content.epson.de/fileadmin/content/files/RSD/downloads/escpos.pdf>`_
        transcribed here for convenience:

        +-----------+----------------------------------+
        | Code Page | Character Code                   |
        +===========+==================================+
        | ``0``     | PC437 (USA: Standard Europe)     |
        +-----------+----------------------------------+
        | ``1``     | Katana                           |
        +-----------+----------------------------------+
        | ``2``     | PC850 (Multilingual)             |
        +-----------+----------------------------------+
        | ``3``     | PC860 (Portuguese)               |
        +-----------+----------------------------------+
        | ``4``     | PC863 (Canadian-French)          |
        +-----------+----------------------------------+
        | ``5``     | PC865 (Nordic)                   |
        +-----------+----------------------------------+
        | ``16``    | WPC1252                          |
        +-----------+----------------------------------+
        | ``17``    | PC866 (Cyrillic #2)              |
        +-----------+----------------------------------+
        | ``18``    | PC852 (Latin 2)                  |
        +-----------+----------------------------------+
        | ``19``    | PC858 (Euro)                     |
        +-----------+----------------------------------+
        | ``20``    | Thai character code 42           |
        +-----------+----------------------------------+
        | ``21``    | Thai character code 11           |
        +-----------+----------------------------------+
        | ``22``    | Thai character code 13           |
        +-----------+----------------------------------+
        | ``23``    | Thai character code 14           |
        +-----------+----------------------------------+
        | ``24``    | Thai character code 16           |
        +-----------+----------------------------------+
        | ``25``    | Thai character code 17           |
        +-----------+----------------------------------+
        | ``26``    | Thai character code 18           |
        +-----------+----------------------------------+
        | ``254``   | User-defined page                |
        +-----------+----------------------------------+
        | ``255``   | User-defined page                |
        +-----------+----------------------------------+

        .. note::

            Be aware of "encoding" attribute versus the code page set.
            Usually they must match, unless you know what you are doing.
            For example, if your encoding is "cp850", then the code page
            set should be "PC850", according to the above table.

            Take a look at the Python documentation for the ``codec``'s
            module `Standard Encodings <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

            Also, check you printer's manual for the code page table.

        :param int code_page: The code page to set. This must be an integer
            randing from 0 to 255, whose meaning depends upon your printer
            model.

        """  # noqa: E501
        if not 0 <= code_page <= 255:
            raise ValueError((
                    'Code page value should be between 0 and 255;'
                    'got: {!r}'
                ).format(code_page))
        self.device.write(b'\x1B\x74' + six.int2byte(code_page))

    def set_font(self, font=FONT_A):
        """Set font to one of :attr:`AVAILABLE_FONTS`."""
        valid_fonts = [param for param, value in AVAILABLE_FONTS]
        if font not in valid_fonts:
            raise ValueError(
                    (
                        'Invalid font: {!r} (valid fonts are {!r})'
                    ).format(font, valid_fonts))
        self.device.write(b'\x1B\x4D' + font)  # ESC M <n>

    def set_mode(
            self,
            font=FONT_A,
            emphasized=False,
            underline=False,
            expanded=False):
        """Set font, emphasized mode, underline mode and expanded mode."""
        commands = []
        param = ByteValue()

        if font in (FONT_A, FONT_B):
            if font == FONT_B:
                param.set_bit(0)
        else:
            # set character font using ESC M (after ESC !)
            commands.append(b'\x1B\x4D' + font)

        if emphasized:
            param.set_bit(3)

        if underline:
            # TODO: control underline thickness using ESC -
            # https://reference.epson-biz.com/modules/ref_escpos/index.php?content_id=24
            param.set_bit(7)

        if expanded:
            param.set_bit(4)
            param.set_bit(5)

        commands.insert(0, b'\x1B\x21' + param.byte)  # ESC !

        for cmd in commands:
            self.device.write(cmd)

    def set_text_size(self, width, height):
        """Set text size to ``width`` and ``height``.

        :param int width: An integer ranging from 0 to 7 (inclusive) whose
            meaning is the magnification of the text in horizontal direction,
            it is, ``0`` for 1x (normal text), ``1`` for 2x, and so on.

        :param int height: An integer ranging from 0 to 7 (inclusive) whose
            meaning is the magnification of the text in vertical direction,
            it is, ``0`` for 1x (normal text), ``1`` for 2x, and so on.

        """
        if (0 <= width <= 7) and (0 <= height <= 7):
            size = 16 * width + height
            self.device.write(b'\x1D\x21' + six.int2byte(size))
        else:
            raise ValueError((
                    'Width and height should be between 0 and 7 '
                    '(1x through 8x of magnification); '
                    'got: width={!r}, height={!r}'
                ).format(width, height))

    def set_expanded(self, flag):
        """Turns on/off expanded mode. Usually this means a text size of 2x
        magnification in both horizontal and vertical directions.

        :param bool flag: If ``True`` sets expanded on.

        """
        param = ByteValue()
        if flag:
            # set character size to double width and height
            param.set_bit(4)  # bits 6, 5, 4 = 0, 0, 1 (x2 width)
            param.set_bit(0)  # bits 2, 1, 0 = 0, 0, 1 (x2 height)
        self.device.write(b'\x1D\x21' + param.byte)  # GS !

    def set_condensed(self, flag):
        """Turns on/off condensed mode by switching between :attr:`FONT_A`
        (normal) and :attr:`FONT_B` (condensed).

        :param bool flag: If ``True`` sets condensed on.

        """
        param = FONT_B if flag else FONT_A
        self.set_font(font=param)

    def set_emphasized(self, flag):
        """Turns on/off emphasized mode. See :meth:`set_double_strike`.

        :param bool flag: If ``True`` sets emphasized on.

        """
        param = b'\x01' if flag else b'\x00'
        self.device.write(b'\x1B\x45' + param)  # ESC E

    def set_double_strike(self, flag):
        """Turns on/off double strike mode. In practice, double strike and
        emphasized modes produces same results.

        :param bool flag: If ``True`` sets double strike on.

        """
        param = b'\x01' if flag else b'\x00'
        self.device.write(b'\x1B\x47' + param)  # ESC G

    def ean8(self, data, **kwargs):
        """Render given data as **JAN-8/EAN-8** barcode symbology.

        :param str data: The JAN-8/EAN-8 data to be rendered.
        """
        if not re.match(r'\d{8}', data):
            raise ValueError((
                    'JAN-8/EAN-8 symbology requires 8 digits of data; '
                    'got {:d} digits: {!r}'
                ).format(len(data), data))
        barcode.validate_barcode_args(**kwargs)
        return self._ean8_impl(data, **kwargs)

    def _ean8_impl(self, data, **kwargs):
        ean8_data = data.encode(self.encoding, self.encoding_errors)
        commands = barcode.gs_k_barcode(
                barcode.JAN8_EAN8,
                ean8_data,
                **kwargs
            )
        for cmd in commands:
            self.device.write(cmd)

        time.sleep(0.25)  # wait for barcode to be printed
        return self.device.read()

    def ean13(self, data, **kwargs):
        """Render given data as **JAN-13/EAN-13** barcode symbology.

        :param str data: The JAN-13/EAN-13 data to be rendered.
        """
        if not re.match(r'\d{13}', data):
            raise ValueError((
                    'JAN-13/EAN-13 symbology requires 13 digits of '
                    'data; got {:d} digits: {!r}'
                ).format(len(data), data))
        barcode.validate_barcode_args(**kwargs)
        return self._ean13_impl(data, **kwargs)

    def _ean13_impl(self, data, **kwargs):
        ean13_data = data.encode(self.encoding, self.encoding_errors)
        commands = barcode.gs_k_barcode(
                barcode.JAN13_EAN13,
                ean13_data,
                **kwargs
            )
        for cmd in commands:
            self.device.write(cmd)

        time.sleep(0.25)  # wait for barcode to be printed
        return self.device.read()

    def code128(self, data, **kwargs):
        """Renders given data as **Code 128** barcode symbology.

        :param str data: The Code 128 data to be rendered.
        :param bytes codeset: Optional. Keyword argument for the subtype (code
            set) to render. Defaults to :attr:`escpos.barcode.CODE128_A`.

        .. warning::

            You should draw up your data according to the subtype (code set).
            The default is **Code 128 A** and there is no way (yet) to mix code
            sets in a single barcode rendering (at least not uniformly).

            Implementations may simply ignore the code set.

        """
        if not re.match(r'^[\x20-\x7F]+$', data):
            raise ValueError((
                    'Invalid Code 128 symbology. Code 128 can encode any '
                    'ASCII character ranging from 32 (20h) to 127 (7Fh); '
                    'got: {!r}'
                ).format(data))
        codeset = kwargs.pop('codeset', barcode.CODE128_A)
        barcode.validate_barcode_args(**kwargs)
        return self._code128_impl(data, codeset=codeset, **kwargs)

    def _code128_impl(self, data, **kwargs):
        codeset = kwargs.get('codeset', barcode.CODE128_A)
        if not is_value_in(barcode.CODE128_CODESETS, codeset):
            raise ValueError('Unknown Code 128 code set: {!r}'.format(codeset))

        encoded_data = (
                b'\x7B'
                + codeset
                + data.encode(self.encoding, self.encoding_errors)
            )  # {<codeset><data>
        commands = barcode.gs_k_barcode(
                barcode.CODE128,
                encoded_data,
                **kwargs
            )
        for cmd in commands:
            self.device.write(cmd)

        time.sleep(0.25)  # wait for barcode to be printed
        return self.device.read()

    def qrcode(self, data, **kwargs):
        """Render given data as `QRCode <http://www.qrcode.com/en/>`_.

        :param str data: Data (QRCode contents) to be rendered.
        """
        barcode.validate_qrcode_args(**kwargs)
        return self._qrcode_impl(data, **kwargs)

    def _qrcode_impl(self, data, **kwargs):
        qr_data = data.encode(self.encoding, self.encoding_errors)

        # compute HI,LO bytes for the number of bytes (parameters) after `pH`;
        # this is possibly the safest way, but alternatives are:
        #
        #     size_H = num_bytes // 256 # (!) integer division (rounding down)
        #     size_L = num_bytes % 256
        #
        # or:
        #
        #     size_H, size_L = divmod(num_bytes, 256)
        #
        num_bytes = 3 + len(qr_data)  # 3 is the number of bytes after `pH`
        size_H = (num_bytes >> 8) & 0xff
        size_L = num_bytes & 0xff

        commands = [
                b'\x1D\x28\x6B'  # GS(k
                + six.int2byte(size_L)
                + six.int2byte(size_H)
                + b'\x31'  # cn (49 <=> 0x31 <=> QRCode)
                + b'\x50'  # fn (80 <=> 0x50 <=> store symbol in memory)
                + b'\x30'  # m (48 <=> 0x30 <=> literal value)
                + qr_data
            ]

        commands.append(
                b'\x1D\x28\x6B'  # GS(k
                + b'\x03'  # pL
                + b'\x00'  # pH
                + b'\x31'  # cn (49 <=> 0x31 <=> QRCode)
                + b'\x45'  # fn (69 <=> 0x45 <=> error correction)
                + _get_qrcode_error_correction(**kwargs)
            )

        commands.append(
                b'\x1D\x28\x6B'  # GS(k
                + b'\x03'  # pL
                + b'\x00'  # pH
                + b'\x31'  # cn (49 <=> 0x31 <=> QRCode)
                + b'\x43'  # fn (67 <=> 0x43 <=> module size)
                + _get_qrcode_module_size(**kwargs)
            )

        commands.append(
                b'\x1D\x28\x6B'  # GS(k
                + b'\x03'  # pL
                + b'\x00'  # pH
                + b'\x31'  # cn (49 <=> 0x31 <=> QRCode)
                + b'\x51'  # fn (81 <=> 0x51 <=> print 2D symbol)
                + b'\x30'  # m (48 <=> 0x30 <=> literal value)
            )

        for cmd in commands:
            self.device.write(cmd)

        time.sleep(1)  # sleeps one second for qrcode to be printed
        return self.device.read()

    def cut(self, partial=True, feed=0):
        """Trigger cutter to perform partial (default) or full paper cut.

        :param bool partial: Optional. Indicates a partial (``True``, the
            default value) or a full cut (``False``).

        :param int feed: Optional. Value from 0 (default) to 255 (inclusive).
            This value should be multiple of the vertical motion unit, feeding
            paper "until current position reaches the cutter".
            For details, visit `GS V <https://www.epson-biz.com/modules/ref_escpos/index.php?content_id=87>`_
            command documentation.

        """  # noqa: E501
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
            func_b = b'\x42' if partial else b'\x41'  # function B
            feed_n = six.int2byte(feed)
            self.device.write(b'\x1D\x56' + func_b + feed_n)  # GS V m n

    def kick_drawer(self, port=0, **kwargs):
        """Kick drawer connected to the given port.

        In this implementation, cash drawers are identified according to the
        port in which they are connected. This relation between drawers and
        ports does not exists in the ESC/POS specification and it is just a
        design decision to normalize cash drawers handling. From the user
        application perspective, drawers are simply connected to port 0, 1, 2,
        and so on.

        If printer does not have this feature then no exception should be
        raised.

        :param int number: The port number to kick drawer (default is ``0``).

        :raises CashDrawerException: If given port does not exists.
        """
        if self.hardware_features.get(feature.CASHDRAWER_PORTS, False):
            # if feature is available assume at least one port is available
            max_ports = self.hardware_features.get(
                    feature.CASHDRAWER_AVAILABLE_PORTS, 1
                )

            if port not in range(max_ports):
                raise CashDrawerException((
                        'invalid cash drawer port: {!r} (available '
                        'ports are {!r})'
                    ).format(port, list(range(max_ports))))

            return self._kick_drawer_impl(port=port, **kwargs)

    def _kick_drawer_impl(self, port=0, **kwargs):
        if port not in range(2):
            raise CashDrawerException((
                    'invalid cash drawer port: {!r}'
                ).format(port))

        param = b'\x00' if port == 0 else b'\x01'  # pulse to pin 2 or 5
        self.device.write(b'\x1B\x70' + param)


class TMT20(GenericESCPOS):
    """Epson TM-T20 thermal printer."""

    model = _Model(name='Epson TM-T20', vendor=VENDOR)

    def __init__(self, device, features={}, **kwargs):
        super(TMT20, self).__init__(device, **kwargs)
        self.hardware_features.update({
                feature.CUTTER: True,
                feature.CASHDRAWER_PORTS: True,
                feature.CASHDRAWER_AVAILABLE_PORTS: 1,
            })
        self.hardware_features.update(features)


def _get_qrcode_error_correction(**kwargs):
    # adapt from PyESCPOS to Epson's own QRCode ECC level byte value
    return QRCODE_ERROR_CORRECTION_MAP.get(
            kwargs.get(
                    'qrcode_ecc_level',
                    barcode.QRCODE_ERROR_CORRECTION_L
                )
        )


def _get_qrcode_module_size(**kwargs):
    # adapt from PyESCPOS to Epson's own QRCode module size byte value
    return QRCODE_MODULE_SIZE_MAP.get(
            kwargs.get(
                    'qrcode_module_size',
                    barcode.QRCODE_MODULE_SIZE_4
                )
        )
