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

import select
import socket

from six.moves import range

from .. import config
from ..exceptions import NonReadableSocketError
from ..exceptions import NonWritableSocketError
from ..retry import backoff


DEFAULT_READ_BUFSIZE = 4096

_RETRY_EXCEPTIONS = (
        NonReadableSocketError,
        NonWritableSocketError,
        socket.error,)


config.configure()


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


    def __init__(self, host, port,
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


    def _raise_with_details(self, message, exctype=RuntimeError):
        raise exctype('{}: {!r} (host={!r}, port={!r}, '
                'socket address family={!r}, socket type={!r})'.format(
                        message,
                        self.socket,
                        self.host_name,
                        self.port_number,
                        self.address_family,
                        self.socket_type))


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
                    [self.socket,],
                    [self.socket,], self.select_timeout)
            if writable:
                break
            else:
                self._reconnect()
        else:
            self._raise_with_details('cannot read from socket', exctype=NonWritableSocketError)


    def _assert_readable(self):
        # check if we can read from socket; if not, make one attempt to
        # reconnect before raising an exception
        if self.socket is None:
            self._reconnect()

        for tries in range(2):
            readable, writable, in_error = select.select(
                    [self.socket,],
                    [],
                    [self.socket,], self.select_timeout)
            if readable:
                break
            else:
                self._reconnect()
        else:
            self._raise_with_details('cannot read from socket', exctype=NonReadableSocketError)


    def _raw_release(self):
        if self.socket is not None:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.socket = None


    def _raw_catch(self):
        # [*] TCP_NODELAY disable Nagle's algorithm so that even small TCP
        # packets will be sent immediately.
        # https://en.wikipedia.org/wiki/Nagle's_algorithm
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # [*]
        self.socket.connect((self.host_name, self.port_number))


    def _raw_write(self, data):
        self._assert_writable()
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
        except:
            return ''


    @backoff(
            max_tries=config.retry.max_tries,
            delay=config.retry.delay,
            factor=config.retry.factor,
            exceptions=_RETRY_EXCEPTIONS)
    def release(self):
        return self._raw_release()


    @backoff(
            max_tries=config.retry.max_tries,
            delay=config.retry.delay,
            factor=config.retry.factor,
            exceptions=_RETRY_EXCEPTIONS)
    def catch(self):
        return self._raw_catch()


    @backoff(
            max_tries=config.retry.max_tries,
            delay=config.retry.delay,
            factor=config.retry.factor,
            exceptions=_RETRY_EXCEPTIONS)
    def write(self, data):
        return self._raw_write(data)


    @backoff(
            max_tries=config.retry.max_tries,
            delay=config.retry.delay,
            factor=config.retry.factor,
            exceptions=_RETRY_EXCEPTIONS)
    def read(self):
        return self._raw_read()
