# -*- coding: utf-8 -*-
#
# escpos/tests/test_conn_bt.py
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

import pytest

import bluetooth

from escpos.conn.bt import find_rfcomm_port
from escpos.conn.bt import BluetoothPortDiscoveryError
from escpos.conn.bt import BluetoothConnection


class FakeBluetoothSocket(object):

    def __init__(self, protocol):
        self._protocol = protocol
        self._connected = False
        self._buffer = []


    def connect(self, address):
        self._connected = True


    def shutdown(self, how):
        self._connected = False


    def close(self):
        self._connected = False


    def send(self, data):
        self._assert_connected()
        self._buffer.append(data)
        return len(data)


    def recv(self):
        self._assert_connected()
        return ''.join(self._buffer)


    def _assert_connected(self):
        assert self._connected, 'Connection is closed or has been shutdown'


def test_find_rfcomm_port(monkeypatch):
    def mockreturn(address=None, name=None, uuid=None):
        return [{
                'description': None,
                'host': '00:01:02:03:04:05',
                'name': 'SerialPort',
                'port': 4,
                'profiles': [('1101', 256)],
                'protocol': 'RFCOMM',
                'provider': None,
                'service-classes': ['1101'],
                'service-id': None
            },]

    monkeypatch.setattr(bluetooth, 'find_service', mockreturn)

    port = find_rfcomm_port('00:01:02:03:04:05')
    assert port == 4

    with pytest.raises(BluetoothPortDiscoveryError):
        port = find_rfcomm_port('00:00:00:00:00:00')


def test_find_rfcomm_port_no_services(monkeypatch):
    def mockreturn(address=None, name=None, uuid=None):
        return []
    monkeypatch.setattr(bluetooth, 'find_service', mockreturn)
    with pytest.raises(BluetoothPortDiscoveryError):
        port = find_rfcomm_port('00:00:00:00:00:00')



def test_simple_rxtx(monkeypatch):
    def mockreturn(protocol):
        return FakeBluetoothSocket(protocol)

    monkeypatch.setattr(bluetooth, 'BluetoothSocket', mockreturn)

    conn = BluetoothConnection.create('00:01:02:03:04:05/2')
    assert conn.address == '00:01:02:03:04:05'
    assert conn.port == 2
    assert conn.socket is None

    conn.catch()
    assert conn.socket is not None

    conn.write('The quick brown fox ')
    conn.write('jumps over the lazy dog')
    data = conn.read()
    assert data == 'The quick brown fox jumps over the lazy dog'

    conn.release()
    assert conn.socket is None
