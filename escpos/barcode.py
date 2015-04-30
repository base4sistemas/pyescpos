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

"""
    Barcode normalization parameters/values.

    Implementations of ESC/POS systems should rely on these end-user values
    and then make their best efforts to translate to the implementation
    specific values.
"""

from .helpers import is_value_in


BARCODE_NORMAL_WIDTH = 1
BARCODE_DOUBLE_WIDTH = 2
BARCODE_QUADRUPLE_WIDTH = 3

BARCODE_WIDTHS = (
        (BARCODE_NORMAL_WIDTH, u'Normal width'),
        (BARCODE_DOUBLE_WIDTH, u'Double width'),
        (BARCODE_QUADRUPLE_WIDTH, u'Quadruple width'),
    )
"""
Possible barcode width values.
"""


BARCODE_HRI_NONE = 0
BARCODE_HRI_TOP = 1
BARCODE_HRI_BOTTOM = 2
BARCODE_HRI_BOTH = 3

BARCODE_HRI_POSITIONING = (
        (BARCODE_HRI_NONE, u'No HRI'),
        (BARCODE_HRI_TOP, u'HRI on top of barcode'),
        (BARCODE_HRI_BOTTOM, u'HRI on bottom of barcode'),
        (BARCODE_HRI_BOTH, u'HRI on both top and bottom of bar code'),
    )
"""
Possible barcode HRI (*human readable information*) positionings.
"""


QRCODE_ERROR_CORRECTION_L = 'L'
QRCODE_ERROR_CORRECTION_M = 'M'
QRCODE_ERROR_CORRECTION_Q = 'Q'
QRCODE_ERROR_CORRECTION_H = 'H'

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


_BARCODE_ARGS = {
        'barcode_height':
                lambda v: v in xrange(1, 256),

        'barcode_width':
                lambda v: is_value_in(BARCODE_WIDTHS, v),

        'barcode_hri':
                lambda v: is_value_in(BARCODE_HRI_POSITIONING, v),
    }


_QRCODE_ARGS = {
        'qrcode_module_size':
                lambda v: is_value_in(QRCODE_MODULE_SIZES, v),

        'qrcode_ecc_level':
                lambda v: is_value_in(QRCODE_ERROR_CORRECTION_LEVELS, v),
    }


def validate_barcode_args(**kwargs):
    """
    Validate QRCode keyword arguments.

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
        raise ValueError("Unexpected keyword argument: '{}'".format(argument))


def _validate_kwarg_value(possible_kwargs, argument, value):
    if not possible_kwargs[argument](value):
        raise ValueError("Invalid argument value: {:s}={!s}".format(
                argument, value))

