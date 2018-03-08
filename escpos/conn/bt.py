# -*- coding: utf-8 -*-
#
# escpos/conn/bt.py
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

import logging
import socket

import bluetooth

from .. import config
from ..retry import backoff


_RETRY_EXCEPTIONS = (
        bluetooth.BluetoothError,)


config.configure()


logger = logging.getLogger('escpos.conn.bt')


class BluetoothConnectionError(Exception):
    pass


class BluetoothPortDiscoveryError(BluetoothConnectionError):
    pass


def find_rfcomm_port(address):
    services = bluetooth.find_service(address=address)
    if not services:
        raise BluetoothPortDiscoveryError('cannot find address: {!r}'.format(address))

    for service in services:
        if service['host'] == address and service['protocol'] == 'RFCOMM':
            return service['port']

    raise BluetoothPortDiscoveryError('cannot find RFCOMM port for address: {!r}'.format(address))



class BluetoothConnection(object):
    """Implements a basic bluetooth RFCOMM communication façade."""

    SETTINGS_EXAMPLE = '00:01:02:03:04:05/1'


    @classmethod
    def create(cls, settings):
        """Create a :class:`BluetoothConnection`:

        .. sourcecode:: python

            from escpos import BluetoothConnection
            from escpos.impl.epson import GenericESCPOS

            conn = BluetoothConnection.create('00:01:02:03:04:05')
            printer = GenericESCPOS(conn)
            printer.init()
            printer.text('Hello World!')

        :param str settings: Bluetooth settings. You must specify bluetooth
            address as six hexadecimal octets, like ``00:01:02:03:04:05``.
            You can also specify a port number after address using a forward
            slash, like ``00:01:02:03:04:05/2``. If there is no port number,
            this method will use SPD (*Service Discovery Protocol*) to find a
            suitable port number for the given address at RFCOMM protocol.

        :raises BluetoothPortDiscoveryError: If port is not specified and the
            algorithm cannot find a RFCOMM port for the given address.
        """
        fields = settings.rsplit('/', 1)
        address = fields[0]

        if len(fields) == 1:
            port = find_rfcomm_port(address)
        else:
            try:
                port = int(fields[1])
            except ValueError:
                raise BluetoothConnectionError('Invalid settings: {!r}'.format(settings))

        return cls(address, port=port)


    def __init__(self, address, port=1):
        super(BluetoothConnection, self).__init__()
        self.socket = None
        self.address = address
        self.port = port


    @backoff(
            max_tries=config.retry.max_tries,
            delay=config.retry.delay,
            factor=config.retry.factor,
            exceptions=_RETRY_EXCEPTIONS)
    def release(self):
        if self.socket is not None:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.socket = None


    @backoff(
            max_tries=config.retry.max_tries,
            delay=config.retry.delay,
            factor=config.retry.factor,
            exceptions=_RETRY_EXCEPTIONS)
    def catch(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.connect((self.address, self.port))


    @backoff(
            max_tries=config.retry.max_tries,
            delay=config.retry.delay,
            factor=config.retry.factor,
            exceptions=_RETRY_EXCEPTIONS)
    def write(self, data):
        totalsent = 0
        while totalsent < len(data):
            sent = self.socket.send(data[totalsent:])
            if sent == 0:
                self._raise_with_details('socket connection broken')
            totalsent += sent


    @backoff(
            max_tries=config.retry.max_tries,
            delay=config.retry.delay,
            factor=config.retry.factor,
            exceptions=_RETRY_EXCEPTIONS)
    def read(self):
        try:
            return self.socket.recv()
        except:
            logger.exception('read error')
            return ''
