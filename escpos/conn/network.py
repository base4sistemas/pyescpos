# -*- coding: utf-8 -*-
#
# escpos/conn/network.py
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

import errno
import logging
import os
import select
import socket

from future.utils import python_2_unicode_compatible
from six.moves import range

from .. import config
from ..exceptions import NonReadableSocketError
from ..exceptions import NonWritableSocketError
from ..helpers import hexdump
from ..retry import backoff


DEFAULT_READ_BUFSIZE = 4096

_RETRY_EXCEPTIONS = (
        NonReadableSocketError,
        NonWritableSocketError,
        socket.error,
    )


def _network_exception_handler(ex):
    # Retry for any expected exception
    return isinstance(ex, _RETRY_EXCEPTIONS)


def _is_socket_error_exception(ex):
    # Test for broken pipe (EPIPE), transport endpoint not connected (ENOTCONN)
    # or connection reset by peer (ECONNRESET)
    flag = (
            isinstance(ex, socket.error)
            and ex.errno in (
                    errno.EPIPE,
                    errno.ENOTCONN,
                    errno.ECONNRESET
                )
        )
    return flag


def _network_exception_handler_for_write(ex):
    # Deals with very specific socket errors upon write operations
    if _is_socket_error_exception(ex):
        logger.debug('caught %r: %s', ex.errno, os.strerror(ex.errno))
        return True  # retry
    else:
        # not a specific socket error, retry for other expected
        # exceptions if its is the case
        return isinstance(ex, _RETRY_EXCEPTIONS)


logger = logging.getLogger('escpos.conn.network')


@python_2_unicode_compatible
class NetworkConnection(object):
    """Implements a potentially resilient network TCP/IP connection."""

    SETTINGS_EXAMPLE = '192.168.0.100:9100'

    @classmethod
    def create(cls, setting, **kwargs):
        """Instantiate a :class:`NetworkConnection` (or subclass) object based
        on a given host name and port number (eg. ``192.168.0.205:9100``).
        """
        host, port = setting.rsplit(':', 1)
        return cls(host, int(port), **kwargs)

    def __init__(
            self,
            host,
            port,
            address_family=socket.AF_INET,
            socket_type=socket.SOCK_STREAM,
            select_timeout=1.0,
            read_buffer_size=DEFAULT_READ_BUFSIZE):

        super(NetworkConnection, self).__init__()
        self.socket = None
        self.host_name = host
        self.port_number = port
        self.address_family = address_family
        self.socket_type = socket_type
        self.select_timeout = select_timeout
        self.read_buffer_size = read_buffer_size

    def __del__(self):
        self._raw_release()

    def __repr__(self):
        content = (
                '{}({!r}, {!r}, address_family={!r}, socket_type={!r}, '
                'select_timeout={!r}, read_buffer_size={!r})'
            ).format(
                self.__class__.__name__,
                self.host_name,
                self.port_number,
                self.address_family,
                self.socket_type,
                self.select_timeout,
                self.read_buffer_size
            )
        return content

    def __str__(self):
        return '{}:{}'.format(self.host_name, self.port_number)

    def _raise_with_details(self, message, exctype=RuntimeError):
        raise exctype((
                '{}: {!r} (host={!r}, port={!r}, '
                'socket address family={!r}, socket type={!r})'
            ).format(
                message,
                self.socket,
                self.host_name,
                self.port_number,
                self.address_family,
                self.socket_type
            ))

    def _reconnect(self):
        self._raw_release()
        self._raw_catch()

    def _assert_writable(self):
        # check if we can write to socket; if not, make one attempt to
        # reconnect before raising an exception
        if self.socket is None:
            self._reconnect()

        for tries in range(2):
            readable, writable, in_error = select.select(
                    [],
                    [self.socket],
                    [self.socket], self.select_timeout)
            if writable:
                break
            else:
                self._reconnect()
        else:
            self._raise_with_details(
                    'cannot read from socket', exctype=NonWritableSocketError
                )

    def _assert_readable(self):
        # check if we can read from socket; if not, make one attempt to
        # reconnect before raising an exception
        if self.socket is None:
            self._reconnect()

        for tries in range(2):
            readable, writable, in_error = select.select(
                    [self.socket],
                    [],
                    [self.socket], self.select_timeout)
            if readable:
                break
            else:
                self._reconnect()
        else:
            self._raise_with_details(
                    'cannot read from socket', exctype=NonReadableSocketError
                )

    def _raw_release(self):
        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:  # noqa
                pass

            try:
                self.socket.close()
            except:  # noqa
                pass

            self.socket = None

    def _raw_catch(self):
        # Constant socket.TCP_NODELAY disables Nagle's algorithm so that even
        # small TCP packets will be sent immediately.
        # See: https://en.wikipedia.org/wiki/Nagle's_algorithm
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.connect((self.host_name, self.port_number))

    def _raw_write(self, data):
        self._assert_writable()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('sending to %s:\n%s', self, hexdump(data))
        totalsent = 0
        while totalsent < len(data):
            sent = self.socket.send(data[totalsent:])
            if sent == 0:
                self._raise_with_details('socket connection broken')
            totalsent += sent

    def _raw_read(self):
        try:
            self._assert_readable()
            return self.socket.recv(self.read_buffer_size)
        except:  # noqa: E722
            return None

    def _before_delay_handler_for_write(self, ex):
        if _is_socket_error_exception(ex):
            self._raw_release()

    def _after_delay_handler_for_write(self, ex):
        if _is_socket_error_exception(ex):
            self._raw_catch()

    def release(self):
        @backoff(
                max_tries=config.BACKOFF_MAXTRIES,
                delay=config.BACKOFF_DELAY,
                factor=config.BACKOFF_FACTOR,
                exception_handler=_network_exception_handler)
        def _release():
            return self._raw_release()
        return _release()

    def catch(self):
        @backoff(
                max_tries=config.BACKOFF_MAXTRIES,
                delay=config.BACKOFF_DELAY,
                factor=config.BACKOFF_FACTOR,
                exception_handler=_network_exception_handler)
        def _catch():
            return self._raw_catch()
        return _catch()

    def write(self, data):
        @backoff(
                max_tries=config.BACKOFF_MAXTRIES,
                delay=config.BACKOFF_DELAY,
                factor=config.BACKOFF_FACTOR,
                exception_handler=_network_exception_handler_for_write,
                before_delay_handler=self._before_delay_handler_for_write,
                after_delay_handler=self._after_delay_handler_for_write)
        def _write():
            return self._raw_write(data)
        return _write()

    def read(self):
        @backoff(
                max_tries=config.BACKOFF_MAXTRIES,
                delay=config.BACKOFF_DELAY,
                factor=config.BACKOFF_FACTOR,
                exception_handler=_network_exception_handler)
        def _read():
            return self._raw_read()
        return _read()
