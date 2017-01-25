# -*- coding: utf-8 -*-
#
# escpos/tests/test_bematech.py
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

import pytest

from escpos import feature
from escpos.barcode import BARCODE_NORMAL_WIDTH
from escpos.barcode import BARCODE_HRI_BOTTOM
from escpos.exceptions import CashDrawerException
from escpos.impl.bematech import MP4200TH

# TODO: Implement tests for inherited methods so we can detect when changes
#       in the base implementation are potentially breaking the specific
#       implementation.
#

@pytest.fixture(scope='module')
def printer():
    return MP4200TH(pytest.FakeDevice())


def test_has_model_attr(printer):
    assert hasattr(printer, 'model')


def test_init(printer):
    printer.init() # inherited from `escpos.impl.epson.GenericESCPOS`
    assert printer.device.write_buffer == '\x1B\x40'


def test_expanded(printer):
    printer.set_expanded(True)
    assert printer.device.write_buffer == '\x1B\x57\x31'

    printer.set_expanded(False)
    assert printer.device.write_buffer == '\x1B\x57\x30'


def test_condensed(printer):
    printer.set_condensed(True)
    assert printer.device.write_buffer == '\x1B\x0F'

    printer.set_condensed(False)
    assert printer.device.write_buffer == '\x1B\x48'


def test_emphasized(printer):
    printer.set_emphasized(True)
    assert printer.device.write_buffer == '\x1B\x45'

    printer.set_emphasized(False)
    assert printer.device.write_buffer == '\x1B\x46'


def test_cut(printer):
    printer.cut(partial=True)
    assert printer.device.write_buffer == '\x1B\x6D'

    printer.cut(partial=False)
    assert printer.device.write_buffer == '\x1B\x69'


def test_code128(printer):
    printer.code128('123EGGS')
    assert printer.device.write_buffer == '\x1D\x6B\x49\x07123EGGS'

    # Bematech MP-4200 TH does not support Code128 code sets;
    # keyword argument `codeset` will be ignored
    printer.code128('123EGGS',
            barcode_height=90,
            barcode_width=BARCODE_NORMAL_WIDTH,
            barcode_hri=BARCODE_HRI_BOTTOM)

    assert printer.device.write_buffer == ''.join([
            '\x1D\x68\x5A',    # barcode height
            '\x1D\x77\x02',    # barcode width
            '\x1D\x48\x02',    # barcode HRI
            '\x1D\x6B\x49\x07123EGGS',])


def test_qrcode(printer):
    # Bematech's documentation about QRCode is not clear, at least at the
    # time I wrote this code. Thus `qrcode` method simple does not honor
    # expected QRCode arguments. Read the warning in `qrcode` implementation
    # if you want more details.
    data = 'http://www.example.com'
    size_L = len(data) % 255
    size_H = len(data) // 255

    printer.qrcode(data)
    assert printer.device.write_buffer == ''.join([
            '\x1D\x6B\x51', # QRCode command
            '\x03\x08\x08\x01', # unknown parameter values,
            chr(size_L), # LO data length
            chr(size_H), # HI data length
            data,])


def test_cash_drawer(printer):
    printer.kick_drawer(port=0) # default duration should be 200ms (C8h)
    assert printer.device.write_buffer == '\x1B\x76\xC8'

    printer.kick_drawer(port=0, duration=250) # max duration 250ms (FAh)
    assert printer.device.write_buffer == '\x1B\x76\xFA'

    printer.kick_drawer(port=0, duration=50) # min duration 50ms (32h)
    assert printer.device.write_buffer == '\x1B\x76\x32'

    with pytest.raises(ValueError):
        # duration lower than minimum duration
        printer.kick_drawer(port=0, duration=49)

    with pytest.raises(ValueError):
        # duration higher than maximum duration
        printer.kick_drawer(port=0, duration=251)

    with pytest.raises(CashDrawerException):
        # Bematech MP-4200 TH has only one cash drawer port
        printer.kick_drawer(port=1)


def test_two_cash_drawer_ports():
    # since ESC/Bematech command set supports up to 2 ports
    printer = MP4200TH(pytest.FakeDevice(), {
            feature.CASHDRAWER_AVAILABLE_PORTS: 2
        })

    printer.kick_drawer(port=1) # default duration should be 200ms (0xC8)
    assert printer.device.write_buffer == '\x1B\x80\xC8'


def test_with_more_cash_drawer_ports_than_escbematech_supports():
    # although we set available cash ports to three ports, ESC/Bematech
    # command set only supports two ports
    printer = MP4200TH(pytest.FakeDevice(), {
            feature.CASHDRAWER_AVAILABLE_PORTS: 3
        })

    with pytest.raises(CashDrawerException):
        printer.kick_drawer(port=3)
