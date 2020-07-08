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
from __future__ import print_function
from __future__ import unicode_literals

import six
from six.moves import range

from .helpers import is_value_in

"""Barcode normalization parameters/values.

Implementations of ESC/POS systems should rely on these end-user values
and then make their best efforts to translate to the implementation
specific values.
"""


NUL_TERM_UPC_A = b'\x00'
NUL_TERM_UPC_E = b'\x01'
NUL_TERM_JAN13_EAN13 = b'\x02'
NUL_TERM_JAN8_EAN8 = b'\x03'
NUL_TERM_CODE39 = b'\x04'
NUL_TERM_ITF = b'\x05'
NUL_TERM_CODABAR_NW_7 = b'\x06'

NUL_TERM_SYMBOLOGIES = (
        (NUL_TERM_UPC_A, 'UPC-A'),
        (NUL_TERM_UPC_E, 'UPC-E'),
        (NUL_TERM_JAN13_EAN13, 'JAN-13/EAN-13'),
        (NUL_TERM_JAN8_EAN8, 'JAN-8/EAN-8'),
        (NUL_TERM_CODE39, 'Code 39'),
        (NUL_TERM_ITF, 'ITF-14'),
        (NUL_TERM_CODABAR_NW_7, 'Codabar NW-7'),
    )


UPC_A = b'A'
UPC_E = b'B'
JAN13_EAN13 = b'C'
JAN8_EAN8 = b'D'
CODE39 = b'E'
ITF = b'F'
CODABAR_NW_7 = b'G'
CODE93 = b'H'
CODE128 = b'I'
GS1_128 = b'J'
GS1_DATABAR_OMNIDIRECTIONAL = b'K'
GS1_DATABAR_TRUNCATED = b'L'
GS1_DATABAR_LIMITED = b'M'
GS1_DATABAR_EXPANDED = b'N'

SYMBOLOGIES = (
        (UPC_A, 'UPC-A'),
        (UPC_E, 'UPC-E'),
        (JAN13_EAN13, 'JAN-13/EAN-13'),
        (JAN8_EAN8, 'JAN-8/EAN-8'),
        (CODE39, 'Code 39'),
        (ITF, 'ITF-14'),
        (CODABAR_NW_7, 'Codabar NW-7'),
        (CODE93, 'Code 93'),
        (CODE128, 'Code 128'),
        (GS1_128, 'GS1-128 (UCC/EAN-128)'),
        (GS1_DATABAR_OMNIDIRECTIONAL, 'GS1 DataBar Omnidirectional'),
        (GS1_DATABAR_TRUNCATED, 'GS1 DataBar Truncated'),
        (GS1_DATABAR_LIMITED, 'GS1 DataBar Limited'),
        (GS1_DATABAR_EXPANDED, 'GS1 DataBar Expanded'),
    )


BARCODE_NORMAL_WIDTH = 1
BARCODE_DOUBLE_WIDTH = 2
BARCODE_QUADRUPLE_WIDTH = 3

BARCODE_WIDTHS = (
        (BARCODE_NORMAL_WIDTH, 'Normal width'),
        (BARCODE_DOUBLE_WIDTH, 'Double width'),
        (BARCODE_QUADRUPLE_WIDTH, 'Quadruple width'),
    )
"""
Possible barcode width values.
"""


BARCODE_HRI_NONE = 0
BARCODE_HRI_TOP = 1
BARCODE_HRI_BOTTOM = 2
BARCODE_HRI_BOTH = 3

BARCODE_HRI_POSITIONING = (
        (BARCODE_HRI_NONE, 'No HRI'),
        (BARCODE_HRI_TOP, 'HRI on top of barcode'),
        (BARCODE_HRI_BOTTOM, 'HRI on bottom of barcode'),
        (BARCODE_HRI_BOTH, 'HRI on both top and bottom of bar code'),
    )
"""
Possible barcode HRI (*human readable information*) positionings.
"""


CODE128_A = b'A'
CODE128_B = b'B'
CODE128_C = b'C'

CODE128_CODESETS = (
        (CODE128_A, 'Code 128 A'),
        (CODE128_B, 'Code 128 B'),
        (CODE128_C, 'Code 128 C'),
    )

QRCODE_ERROR_CORRECTION_L = b'L'
QRCODE_ERROR_CORRECTION_M = b'M'
QRCODE_ERROR_CORRECTION_Q = b'Q'
QRCODE_ERROR_CORRECTION_H = b'H'

QRCODE_ERROR_CORRECTION_LEVELS = (
        (QRCODE_ERROR_CORRECTION_L, 'Level L (~7%)'),
        (QRCODE_ERROR_CORRECTION_M, 'Level M (~15%)'),
        (QRCODE_ERROR_CORRECTION_Q, 'Level Q (~25%)'),
        (QRCODE_ERROR_CORRECTION_H, 'Level H (~30%)'),
    )
"""
QRCode possible error correction levels for ``qrcode_ecc_level`` keyword
argument. See http://www.qrcode.com/en/about/error_correction.html.
"""


QRCODE_MODULE_SIZE_4 = 4
QRCODE_MODULE_SIZE_5 = 5
QRCODE_MODULE_SIZE_6 = 6
QRCODE_MODULE_SIZE_7 = 7
QRCODE_MODULE_SIZE_8 = 8

QRCODE_MODULE_SIZES = (
        (QRCODE_MODULE_SIZE_4, '4-dot'),
        (QRCODE_MODULE_SIZE_5, '5-dot'),
        (QRCODE_MODULE_SIZE_6, '6-dot'),
        (QRCODE_MODULE_SIZE_7, '7-dot'),
        (QRCODE_MODULE_SIZE_8, '8-dot'),
    )
"""
QRCode possible module sizes for ``qrcode_module_size`` keyword argument.
See http://www.qrcode.com/en/howto/cell.html.
"""


_BARCODE_ARGS = dict(
        barcode_height=lambda v: v in range(1, 256),
        barcode_width=lambda v: is_value_in(BARCODE_WIDTHS, v),
        barcode_hri=lambda v: is_value_in(BARCODE_HRI_POSITIONING, v)
    )

_QRCODE_ARGS = dict(
        qrcode_module_size=lambda v: is_value_in(QRCODE_MODULE_SIZES, v),
        qrcode_ecc_level=lambda v: is_value_in(
                QRCODE_ERROR_CORRECTION_LEVELS, v)
    )


def gs_k_barcode_configure(**kwargs):
    commands = []

    if 'barcode_height' in kwargs:
        barcode_height = six.int2byte(kwargs.get('barcode_height'))
        commands.append(b'\x1D\x68' + barcode_height)

    if 'barcode_width' in kwargs:
        gs_k_widths = {
                # (!) adapt from PyESCPOS to 'GS k' standard width byte value
                BARCODE_NORMAL_WIDTH: 2,
                BARCODE_DOUBLE_WIDTH: 3,
                BARCODE_QUADRUPLE_WIDTH: 4,
            }
        barcode_width = gs_k_widths.get(kwargs.get('barcode_width'))
        commands.append(b'\x1D\x77' + six.int2byte(barcode_width))

    if 'barcode_hri' in kwargs:
        values = {
                # (!) adapt from PyESCPOS to 'GS k' standard HRI byte value
                BARCODE_HRI_NONE: 0,
                BARCODE_HRI_TOP: 1,
                BARCODE_HRI_BOTTOM: 2,
                BARCODE_HRI_BOTH: 3,
            }
        barcode_hri = values.get(kwargs.get('barcode_hri'))
        commands.append(b'\x1D\x48' + six.int2byte(barcode_hri))

    return commands


def gs_k_barcode(symbology, data, **kwargs):
    """Build standard ESC/POS barcode through ``GS k`` command set. Keyword
    arguments can be used to configure barcode height, bar widths and HRI
    positioning. User applications should not use this function. This function
    is provided as an ESC/POS "standard barcode command set" to be used by
    specific implementations.

    :param bytes symbology: The symbology to build. Should be one of the
        constants in :attr:`NUL_TERM_SYMBOLOGIES` or :attr:`SYMBOLOGIES`.

    :param bytes data: The barcode data. You should draw up your data
        according to the symbology. If you do not want to worry about data
        formating then you should use barcode methods provided by the
        reference ESC/POS implementation
        :class:`~escpos.impl.epson.GenericESCPOS` instead of this function.

    :param barcode_height: Optional.
    :param barcode_width: Optional.
    :param barcode_hri: Optional.

    :return: A list of commands (bytes), ready to be sent to the device.
    :rtype: list

    """
    commands = gs_k_barcode_configure(**kwargs)

    if symbology in (k for k, v in NUL_TERM_SYMBOLOGIES):
        commands.append(
                b'\x1D\x6B'
                + symbology
                + data
                + b'\x00'
            )
    else:
        size = len(data)
        commands.append(
                b'\x1D\x6B'
                + symbology
                + six.int2byte(size)
                + data
                + b'\x00'
            )

    return commands


def validate_barcode_args(**kwargs):
    """
    Validate barcode keyword arguments.

    .. sourcecode::

        >>> validate_barcode_args(**{})
        >>> validate_barcode_args(**{'barcode_height': 50})
        >>> validate_barcode_args(**{'barcode_width': BARCODE_NORMAL_WIDTH})
        >>> validate_barcode_args(**{'barcode_hri': BARCODE_HRI_TOP})
        >>> validate_barcode_args(**{
        ...         'barcode_height': 100,
        ...         'barcode_width': BARCODE_DOUBLE_WIDTH,
        ...         'barcode_hri': BARCODE_HRI_BOTH})

        >>> validate_barcode_args(**{'no_bars': 123})
        Traceback (most recent call last):
         ...
        ValueError: Unexpected keyword argument: 'no_bars'

        >>> validate_barcode_args(**{'barcode_height': 0})
        Traceback (most recent call last):
         ...
        ValueError: Invalid argument value: barcode_height=0

    """
    _validate_kwargs(_BARCODE_ARGS, **kwargs)


def validate_qrcode_args(**kwargs):
    """
    Validate QRCode keyword arguments.

    .. sourcecode::

        >>> validate_qrcode_args(**{})
        >>> validate_qrcode_args(**{'qrcode_ecc_level': 'L'})
        >>> validate_qrcode_args(**{'qrcode_module_size': 4})
        >>> validate_qrcode_args(**{
        ...         'qrcode_ecc_level': 'L',
        ...         'qrcode_module_size': 4})

        >>> validate_qrcode_args(**{'oops': 123})
        Traceback (most recent call last):
         ...
        ValueError: Unexpected keyword argument: 'oops'

        >>> validate_qrcode_args(**{'qrcode_ecc_level': 'IMPOSSIBLE'})
        Traceback (most recent call last):
         ...
        ValueError: Invalid argument value: qrcode_ecc_level=IMPOSSIBLE

    """
    _validate_kwargs(_QRCODE_ARGS, **kwargs)


def _validate_kwargs(possible_kwargs, **kwargs):
    for argument, value in kwargs.items():
        _validate_kwarg_name(possible_kwargs, argument)
        _validate_kwarg_value(possible_kwargs, argument, value)


def _validate_kwarg_name(possible_kwargs, argument):
    if argument not in possible_kwargs.keys():
        raise ValueError((
                'Unexpected keyword argument: \'{}\''
            ).format(argument))


def _validate_kwarg_value(possible_kwargs, argument, value):
    if not possible_kwargs[argument](value):
        raise ValueError((
                'Invalid argument value: {}={!r}'
            ).format(argument, value))
