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
from __future__ import print_function
from __future__ import unicode_literals

import functools
import logging
import socket

from future.utils import python_2_unicode_compatible

try:
    import bluetooth
    _lib_bluetooth = True
    _RETRY_EXCEPTIONS = (
            bluetooth.BluetoothError,
        )
except ImportError:
    # PyBluez library is optional
    _lib_bluetooth = False
    _RETRY_EXCEPTIONS = ()

from .. import config
from ..helpers import hexdump
from ..retry import backoff


logger = logging.getLogger('escpos.conn.bt')


class BluetoothConnectionError(Exception):
    pass


class BluetoothPortDiscoveryError(BluetoothConnectionError):
    pass


def depends_on_pybluez_lib(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not _lib_bluetooth:
            raise RuntimeError(
                    'In order to make bluetooth connections you must install '
                    'PyBluez library. Alternatively you may want to install '
                    'PyESCPOS using \'pip install pyescpos[bluetooth]\' to '
                    'automatically install dependencies for bluetooth '
                    'connections.'
                )
        return func(*args, **kwargs)
    return wrapper


@depends_on_pybluez_lib
def find_rfcomm_port(address):

    services = bluetooth.find_service(address=address)
    if not services:
        raise BluetoothPortDiscoveryError(
                'cannot find address: {!r}'.format(address)
            )

    for service in services:
        if service['host'] == address and service['protocol'] == 'RFCOMM':
            return service['port']

    raise BluetoothPortDiscoveryError(
            'cannot find RFCOMM port for address: {!r}'.format(address)
        )


def _bt_exception_handler(ex):
    # Retry for any expected exception
    return isinstance(ex, _RETRY_EXCEPTIONS)


@python_2_unicode_compatible
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
                raise BluetoothConnectionError(
                        'Invalid settings: {!r}'.format(settings)
                    )

        return cls(address, port=port)

    def __init__(self, address, port=1):
        super(BluetoothConnection, self).__init__()
        self.socket = None
        self.address = address
        self.port = port

    def __repr__(self):
        content = '{}({!r}, port={!r})'.format(
                self.__class__.__name__,
                self.address,
                self.port
            )
        return content

    def __str__(self):
        return '{}/{}'.format(self.address, self.port)

    @backoff(
            max_tries=config.BACKOFF_MAXTRIES,
            delay=config.BACKOFF_DELAY,
            factor=config.BACKOFF_FACTOR,
            exception_handler=_bt_exception_handler)
    def release(self):
        if self.socket is not None:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.socket = None

    @depends_on_pybluez_lib
    @backoff(
            max_tries=config.BACKOFF_MAXTRIES,
            delay=config.BACKOFF_DELAY,
            factor=config.BACKOFF_FACTOR,
            exception_handler=_bt_exception_handler)
    def catch(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.connect((self.address, self.port))

    @backoff(
            max_tries=config.BACKOFF_MAXTRIES,
            delay=config.BACKOFF_DELAY,
            factor=config.BACKOFF_FACTOR,
            exception_handler=_bt_exception_handler)
    def write(self, data):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('writing to bluetooth %s:\n%s', self, hexdump(data))
        totalsent = 0
        while totalsent < len(data):
            sent = self.socket.send(data[totalsent:])
            if sent == 0:
                self._raise_with_details('socket connection broken')
            totalsent += sent

    @backoff(
            max_tries=config.BACKOFF_MAXTRIES,
            delay=config.BACKOFF_DELAY,
            factor=config.BACKOFF_FACTOR,
            exception_handler=_bt_exception_handler)
    def read(self):
        try:
            return self.socket.recv()
        except Exception:
            logger.exception('read error')
            return None
