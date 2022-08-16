# -*- coding: utf-8 -*-
#
# pyescpos/conn/__init__.py
#
# Copyright 2018 Base4 Sistemas Ltda ME
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

from collections import namedtuple

import six

from .bt import BluetoothConnection
from .dummy import DummyConnection
from .file import FileConnection
from .network import NetworkConnection
from .serial import SerialConnection
from .usb import USBConnection
from .win32 import Win32Raw


__all__ = [
        'BluetoothConnection',
        'DummyConnection',
        'FileConnection',
        'NetworkConnection',
        'SerialConnection',
        'USBConnection',
        'Win32Raw',
    ]

if six.PY2:
    __all__ = [name.encode('latin-1') for name in __all__]


BLUETOOTH = 'bluetooth'
DUMMY = 'dummy'
FILE = 'file'
NETWORK = 'network'
SERIAL = 'serial'
USB = 'usb'
WIN32 = 'win32'


ConnectionTypeInfo = namedtuple('ConnectionTypeInfo', [
        'name',  # friendly name
        'fqname',  # fully qualified name
        'type',
    ])

CONNECTION_TYPES = (
        (BLUETOOTH, ConnectionTypeInfo(
                name='Bluetooth',
                fqname='pyescpos.conn.bt.BluetoothConnection',
                type=BluetoothConnection)),

        (DUMMY, ConnectionTypeInfo(
                name='Dummy',
                fqname='pyescpos.conn.dummy.DummyConnection',
                type=DummyConnection)),

        (FILE, ConnectionTypeInfo(
                name='File',
                fqname='pyescpos.conn.file.FileConnection',
                type=FileConnection)),

        (NETWORK, ConnectionTypeInfo(
                name='Network',
                fqname='pyescpos.conn.network.NetworkConnection',
                type=NetworkConnection)),

        (SERIAL, ConnectionTypeInfo(
                name='Serial (RS-232)',
                fqname='pyescpos.conn.serial.SerialConnection',
                type=SerialConnection)),

        (USB, ConnectionTypeInfo(
                name='USB',
                fqname='pyescpos.conn.usb.USBConnection',
                type=USBConnection)),

        (WIN32, ConnectionTypeInfo(
                name='WIN32',
                fqname='pyescpos.conn.win32.Win32Raw',
                type=Win32Raw)),

    )
"""Known implementations for connection with printers."""
