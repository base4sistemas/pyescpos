# -*- coding: utf-8 -*-
#
# escpos/showcase.py
#
# Copyright 2020 Base4 Sistemas Ltda ME
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
from __future__ import unicode_literals

import math

from datetime import datetime

from . import barcode
from .impl import epson


def showcase(printer, **kwargs):
    """All printing showcases in one call."""
    printer.justify_center()
    printer.set_expanded(True)
    printer.text(printer.model.name)
    printer.set_expanded(False)
    printer.text(printer.model.vendor)
    printer.justify_left()
    printer.lf()

    fonts_showcase(printer, **kwargs)
    printer.cut()

    modes_and_alignment_showcase(printer, **kwargs)
    printer.cut()

    text_size_showcase(printer, **kwargs)
    printer.cut()

    rulers_showcase(printer)
    printer.cut()

    receipt_showcase(printer)
    printer.cut()

    barcode_showcase(printer, **kwargs)
    printer.cut()

    qrcode_showcase(printer, **kwargs)
    printer.cut()


def fonts_showcase(printer, **kwargs):
    """A showcase of available fonts."""
    _header(printer, 'Fonts')
    font_set = kwargs.get('font_set', epson.AVAILABLE_FONTS)
    for param, name in font_set:
        printer.init()
        printer.set_font(param)
        printer.text(name)
    printer.lf()


def modes_and_alignment_showcase(printer):
    """A showcase for font modes (normal, condensed, emphasized and expanded)
    and alignment (left, centered and right alignment).
    """
    _header(printer, 'Modes and Alignment')

    def print_modes(title):
        printer.set_expanded(True)
        printer.text(title)
        printer.set_expanded(False)

        printer.text('Normal mode')

        printer.set_condensed(True)
        printer.text('Condensed mode')
        printer.set_condensed(False)

        printer.set_emphasized(True)
        printer.text('Emphasized mode')
        printer.set_emphasized(False)

    printer.init()

    printer.justify_right()
    print_modes('Right aligned')
    printer.lf()

    printer.justify_center()
    print_modes('Centered')
    printer.lf()

    printer.justify_left()
    print_modes('Left aligned')
    printer.lf()


def text_size_showcase(printer, **kwargs):
    """A showcase of various text sizes.

    :param str text: Any text eight characters long. If its longer than
        eight chars it will be truncated. If less than eight chars it will
        be completed with "X"s.
    """
    text = kwargs.get('text', 'SPAMEGGS')
    letters = text[:8].ljust(8, 'X')

    _header(printer, 'Text Size')

    printer.init()
    for w, c in zip(range(8), letters):
        printer.set_text_size(w, 7)
        printer.textout(c)

    printer.lf()
    for h, c in zip(range(8), letters):
        printer.set_text_size(w, h)
        printer.textout(c)

    printer.lf(2)


def rulers_showcase(printer):
    """A showcase of various column widths."""
    cols = printer.feature.columns
    n = max(cols.normal, max(cols.condensed, cols.expanded))
    ruler = '....:....!' * n

    _header(printer, 'Rulers')

    printer.init()
    printer.text('Normal ({:d} columns)'.format(cols.normal))
    printer.text(ruler[:cols.normal])
    printer.lf()

    printer.text('Condensed ({:d} columns)'.format(cols.condensed))
    printer.set_condensed(True)
    printer.text(ruler[:cols.condensed])
    printer.set_condensed(False)
    printer.lf()

    printer.text('Expanded ({:d} columns)'.format(cols.expanded))
    printer.set_expanded(True)
    printer.text(ruler[:cols.expanded])
    printer.set_expanded(False)
    printer.lf()


def receipt_showcase(printer):
    """A showcase of a fictional POS receipt."""
    ruler_single = _get_ruler(printer)
    ruler_double = _get_ruler(printer, '=')

    printer.init()
    printer.text(ruler_double)
    printer.set_expanded(True)
    printer.justify_center()
    printer.text('RECEIPT #5678')
    printer.justify_left()
    printer.set_expanded(False)
    printer.text(ruler_single)

    printer.text('{:%x %X} Session #{:d}'.format(datetime.now(), 42))

    item_mask = _build_item_mask(
            printer.feature.columns.condensed,
            alignments='><>^>>',
            column_widths=[
                0.1,
                0.4,
                0.15,
                0.05,
                0.15,
                0.15,
            ]
        )

    data = (
            ('ID', 'Product', 'Qty', '', 'Price', 'Subtotal'),
            ('1234', 'SAMPLE', '2', 'x', '0.25', '0.50'),
            ('1235', 'OTHER SAMPLE', '1', 'x', '1.50', '1.50'),
            ('1237', 'ANOTHER ONE', '3', 'x', '0.75', '2.25'),
        )

    printer.set_condensed(True)
    for row in data:
        printer.text(item_mask.format(*row))

    printer.set_condensed(False)
    printer.text(ruler_single)
    printer.set_emphasized(True)
    printer.text('TOTAL  4.25')
    printer.set_emphasized(False)
    printer.text(ruler_double)
    printer.lf()


def barcode_showcase(printer, **kwargs):
    """A showcase of 1-dimensional barcodes."""
    barcode_height = kwargs.get('barcode_height', 120)
    barcode_width = kwargs.get('barcode_width', barcode.BARCODE_NORMAL_WIDTH)
    barcode_hri = kwargs.get('barcode_hri', barcode.BARCODE_HRI_BOTTOM)

    barcodes = (
            ('EAN-8', 'ean8', '12345670'),
            ('EAN-13', 'ean13', '1234567890128'),
            ('Code128-A', 'code128', '12345'),
        )

    _header(printer, 'Barcodes')

    printer.init()

    for title, method, data in barcodes:
        printer.set_emphasized(True)
        printer.text(title)
        printer.set_emphasized(False)
        getattr(printer, method)(
                data,
                barcode_hri=barcode_hri,
                barcode_height=barcode_height,
                barcode_width=barcode_width
            )
        printer.lf()


def qrcode_showcase(printer, **kwags):
    """A showcase of QRCodes in various configurations."""
    data = kwags.get('data', 'https://github.com/base4sistemas/pyescpos')

    _header(printer, 'QRCode')

    printer.init()

    # showcase all default values
    printer.text('QRCode (all defaults)')
    printer.qrcode(data)
    printer.lf()

    # showcase all possible module size variations
    def _qrcode_ecc_level_l(module_size, title):
        printer.text('QRCode')
        printer.text('Module size: {!r} ({})'.format(module_size, title))
        printer.text('  ECC level: L')
        printer.qrcode(
                data,
                qrcode_module_size=module_size,
                qrcode_ecc_level=barcode.QRCODE_ERROR_CORRECTION_L
            )
        printer.lf()

    for value, title in barcode.QRCODE_MODULE_SIZES:
        _qrcode_ecc_level_l(value, title)

    # showcase all possible error correction level variations
    def _qrcode_module_size_4(ecc_level, ecc_title):
        printer.text('QRCode')
        printer.text('Module size: 4')
        printer.text('  ECC level: {!r} ({})'.format(ecc_level, ecc_title))
        printer.qrcode(
                data,
                qrcode_module_size=barcode.QRCODE_MODULE_SIZE_4,
                qrcode_ecc_level=ecc_level
            )
        printer.lf()

    for value, title in barcode.QRCODE_ERROR_CORRECTION_LEVELS:
        _qrcode_module_size_4(value, title)


def _header(printer, title):
    ruler = _get_ruler(printer)
    printer.init()
    printer.text(ruler)
    printer.justify_center()
    printer.text(title)
    printer.justify_left()
    printer.text(ruler)


def _get_ruler(printer, char='-'):
    return char * printer.feature.columns.normal


def _build_item_mask(width, alignments=None, column_widths=None, gap=1):
    # <alignments> str, for example "<>^" (left, right, center)
    # <column_widths> list(float, ...)
    if len(alignments) != len(column_widths):
        raise ValueError('Alignment spec and number of columns must match')
    if sum(column_widths) > 100:
        raise ValueError('Sum of column widths must not be greater than 100%')
    width = width - (len(alignments) * gap) - gap
    columns = []
    for i, perc in enumerate(column_widths):
        col_len = int(math.ceil(perc * width))
        columns.append('{{:{:s}{:d}s}}'.format(alignments[i], col_len))
    return (' ' * gap).join(columns)
