# -*- coding: utf-8 -*-
#
# escpos/serial.py
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

import os
import sys

import serial as pyserial

from .helpers import TimeoutHelper
from .helpers import chunks
from .helpers import hexdump


DEFAULT_READ_TIMEOUT = 1

DEFAULT_WRITE_TIMEOUT = 1

DEFAULT_PROTOCOL_TIMEOUT = 5


RTSCTS = 'RTSCTS'
DSRDTR = 'DSRDTR'
XONXOFF = 'XONXOFF'

FLOW_CONTROL_PROTOCOLS = (
    (RTSCTS, 'Hardware RTS/CTS'),
    (DSRDTR, 'Hardware DSR/DTR'),
    (XONXOFF, 'Software XOn/XOff'),)


def scan_ports():
    """
    Scan for known serial ports available in the underling system.
    Returns a tuple of tuples where each inner tuple contains the port
    number and port name. For example:

    .. sourcecode:: python

        scan_ports()
        ((0, '/dev/ttyS0'), (1, '/dev/ttyS1'), ...)

    """
    names = []
    for number in xrange(256):
        try:
            # attempt attr `name` for PySerial >= 2.5-rc2,
            # where attr `portstr` is for older PySerial versions
            s = pyserial.Serial(number)
            name = getattr(s, 'name', getattr(s, 'portstr', str(number)))
            names.append((number, name,))
        except:
            pass
    return tuple(names)


def get_port_name(port_number):
    """
    Scans for the given port number and return its name.
    If port number does not exists, returns ``None``.
    """
    for number, name in scan_ports():
        if number == port_number:
            return name
    return None


def get_port_number(port_name):
    """
    Scans for the given port name and return its numeric value.
    If port name cannot be found, returns ``None``. Not that the port name is
    case-sensitive.
    """
    for number, name in scan_ports():
        if name == port_name:
            return number
    return None


def get_baudrates():
    """
    Returns supported baud rates in a Django-like choices tuples.
    """
    baudrates = []
    s = pyserial.Serial()
    for name, value in s.getSupportedBaudrates():
        baudrates.append((value, name,))
    return tuple(baudrates)


def get_databits():
    """
    Returns supported byte sizes in a Django-like choices tuples.
    """
    databits = []
    s = pyserial.Serial()
    for name, value in s.getSupportedByteSizes():
        databits.append((value, name,))
    return tuple(databits)


def get_stopbits():
    """
    Returns supported stop bit lengths in a Django-like choices tuples.
    """
    stopbits = []
    s = pyserial.Serial()
    for name, value in s.getSupportedStopbits():
        stopbits.append((value, name,))
    return tuple(stopbits)


def get_parities():
    """
    Returns supported parities in a Django-like choices tuples.
    """
    parities = []
    s = pyserial.Serial()
    for name, value in s.getSupportedParities():
        parities.append((value, name,))
    return tuple(parities)


def get_protocols():
    """
    Returns available protocols in a Django-like choices tuples.
    """
    return FLOW_CONTROL_PROTOCOLS


class SerialSettings(object):
    """
    Holds serial port configurations.
    """

    def __init__(self, **kwargs):
        self._port = None
        self._baudrate = None
        self._databits = None
        self._stopbits = None
        self._parity = None
        self._protocol = RTSCTS

        # maps kwargs to already defined self attributes
        for key, value in kwargs.items():
            attribute = '_%s' % key
            if not hasattr(self, attribute):
                raise AttributeError('%s has no attribute \'%s\'' % (
                        self.__class__.__name__, key,))
            setattr(self, attribute, value)

        self._portname = ''
        self._fix_port_assignment()


    def __repr__(self):
        value = '%s(port=%s, baudrate=%s, databits=%s, stopbits=%s, '\
                'parity="%s", protocol="%s")' % (
                        self.__class__.__name__,
                        self._port,
                        self._baudrate,
                        self._databits,
                        self._stopbits,
                        self._parity,
                        self._protocol,)
        return value


    def __str__(self):
        # eg: "/dev/ttyS0:9600:8:1:N:RTSCTS"
        value = ':'.join([
                self._portname,
                self._baudrate,
                self._databits,
                self._stopbits,
                self._parity,
                self._protocol,])
        return value


    def __unicode__(self):
        return unicode(self.__str__())


    @property
    def portname(self):
        return self._portname


    @property
    def port(self):
        return self._port


    @port.setter
    def port(self, value):
        for number, name in scan_ports():
            if value == number:
                self._port = number
                self._portname = name
                break
            elif value == name:
                self._port = number
                self._portname = name
                break
        else:
            raise ValueError('Given port name/number does not exists: '
                    '%s (%r)' % (value, value,))


    @property
    def baudrate(self):
        return self._baudrate


    @baudrate.setter
    def baudrate(self, value):
        if value not in [v for v,n in get_baudrates()]:
            raise ValueError('Unsupported baud rate value: %s' % value)
        self._baudrate = value


    @property
    def databits(self):
        return self._databits


    @databits.setter
    def databits(self, value):
        if value not in [v for v,n in get_databits()]:
            raise ValueError('Unsupported byte size value: %s' % value)
        self._databits = value


    @property
    def stopbits(self):
        return self._stopbits


    @stopbits.setter
    def stopbits(self, value):
        if value not in [v for v,n in get_stopbits()]:
            raise ValueError('Unsupported stop bits value: %s' % value)
        self._stopbits = value


    @property
    def parity(self):
        return self._parity


    @parity.setter
    def parity(self, value):
        if value not in [v for v,n in get_parities()]:
            raise ValueError('Unsupported parity value: %s' % value)
        self._parity = value


    @property
    def protocol(self):
        return self._protocol


    @protocol.setter
    def protocol(self, value):
        if value not in [v for v,n in get_protocols()]:
            raise ValueError('Unknown protocol: %s' % value)
        self._protocol = value


    def is_rtscts(self):
        return self.protocol == RTSCTS


    def is_dsrdtr(self):
        return self.protocol == DSRDTR


    def is_xonxoff(self):
        return self.protocol == XONXOFF


    def get_connection(self, **kwargs):
        """Return a serial connection implementation suitable for the specified
        protocol. Raises ``RuntimeError`` if there is no implementation for
        the given protocol.

        .. warn::

            This may be a little bit confusing since there is no effective
            connection but an implementation of a connection pattern.

        """
        if self.is_rtscts():
            return RTSCTSConnection(self, **kwargs)

        if self.is_dsrdtr():
            return DSRDTRConnection(self, **kwargs)

        else:
            raise RuntimeError('Serial protocol "%s" is not available.' % (
                    self.protocol))


    def _fix_port_assignment(self):
        """
        The :attr:`port` attribute can be set either by name or by its numeric
        value. This method attempt to fix the semantics of name/number as its
        extremely convenient.
        """

        port_name = ''
        port_number = None

        if self._port:
            if isinstance(self._port, int):
                port_number = self._port
                port_name = get_port_name(port_number)
            elif isinstance(self._port, basestring):
                port_name = self._port
                port_number = get_port_number(port_name)
            else:
                raise ValueError('Cannot assign port name/number '
                        'based on port assignment type %r' % self._port)

            self._port = port_number
            self._portname = port_name or ''


    @staticmethod
    def as_from(value):
        """
        Constructs an instance of :class:`SerialSettings` from a string
        representation, that looks like ``/dev/ttyS0:9600,8,1,N,RTSCTS``,
        describing, in order, the serial port name, baud rate, byte size,
        stop bits, parity and flow control protocol.

        Valid string representations are (in cases where protocol is not
        specified, RTS/CTS is assumed)::

            COM1:115000,8,1,E
            COM1:115000:8:1:E
            COM4:9600:8:2:O:DSRDTR
            /dev/ttyS0:9600,8,1,N,RTSCTS
            /dev/ttyS0,9600,8,1,N

        """
        keys = ['port','baudrate','databits','stopbits','parity','protocol']
        values = value.replace(',', ':').split(':')

        if len(values) == 5:
            values.append(RTSCTS)

        if len(keys) != len(values):
            raise ValueError('Unknown serial port string format: %s '
                    '(expecting something like "COM1:9600,8,1,N,RTSCTS")' % (
                    value,))

        kwargs = dict(zip(keys, values))
        kwargs['baudrate'] = int(kwargs['baudrate'])
        kwargs['databits'] = int(kwargs['databits'])
        kwargs['stopbits'] = int(kwargs['stopbits'])

        return SerialSettings(**kwargs)


class AbstractSerialConnection(object):

    def __init__(self, settings,
            read_timeout=DEFAULT_READ_TIMEOUT,
            write_timeout=DEFAULT_WRITE_TIMEOUT,
            protocol_timeout=DEFAULT_PROTOCOL_TIMEOUT):

        super(AbstractSerialConnection, self).__init__()

        self.settings = settings
        """Serial settings as an instance of :class:`SerialSettings`."""

        self.comport = None
        """The gateway to the serial communications port, usually an
        instance of ``serial.Serial`` from the **PySerial** library.
        """

        self.read_timeout = read_timeout

        self.write_timeout = write_timeout

        self.protocol_timeout = protocol_timeout

        self.device_encoding = 'CP850'

        self.hex_dump = True


    def __del__(self):
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.close()


    @property
    def protocol_timeout(self):
        return self._protocol_timeout


    @protocol_timeout.setter
    def protocol_timeout(self, value):
        self._protocol_timeout = value
        self._ptimeout = TimeoutHelper(timeout=self._protocol_timeout)


    def is_clear_to_write(self):
        raise NotImplementedError()


    def wait_to_write(self):
        self._ptimeout.set()
        while self._ptimeout.check():
            if self.is_clear_to_write():
                break


    def write(self, data):
        """Write data to serial port."""
        for chunk in chunks(data, 512):
            self.wait_to_write()
            self.comport.write(chunk)
        self.comport.flush()


    def read(self):
        """Read data from serial port and returns a ``bytearray``."""
        data = bytearray()
        while True:
            incoming_bytes = self.comport.inWaiting()
            if incoming_bytes == 0:
                break
            else:
                content = self.comport.read(size=incoming_bytes)
                data.extend(bytearray(content))
        return data


    def catch(self):
        if self.comport is not None:
            if self.comport.isOpen():
                self.comport.close()

        factory = _SerialDumper if self.hex_dump else pyserial.Serial
        port = self.settings.port

        if port is None:
            port = self.settings.portname

        self.comport = factory(
                port=port,
                baudrate=self.settings.baudrate,
                bytesize=self.settings.databits,
                stopbits=self.settings.stopbits,
                parity=self.settings.parity,
                rtscts=self.settings.is_rtscts(),
                dsrdtr=self.settings.is_dsrdtr(),
                xonxoff=self.settings.is_xonxoff(),
                timeout=self.read_timeout,
                writeTimeout=self.write_timeout)

        if not self.comport.isOpen():
            self.comport.open()

        self.comport.setRTS(level=1)
        self.comport.setDTR(level=1)
        self.comport.flushInput()
        self.comport.flushOutput()


    def unicode_to_device_encoding(self, unicode_string):
        return unicode_string.encode('utf-8').decode(self.device_encoding)


    def unicode_to_bytearray(self, unicode_string, errors='ignore'):
        device_encoded_string = self.unicode_to_device_encoding(unicode_string)
        return bytearray(device_encoded_string,
                encoding=self.device_encoding,
                errors=errors)


class RTSCTSConnection(AbstractSerialConnection):
    """Implements a RTS/CTS aware connection."""

    def is_clear_to_write(self):
        return self.comport.getCTS()


class DSRDTRConnection(AbstractSerialConnection):
    """Implements a DSR/DTR aware connection."""

    def is_clear_to_write(self):
        return self.comport.getDSR()


class _SerialDumper(pyserial.Serial):
    """
    This class is used as a wrapper for ``pyserial.Serial`` to allow dumping
    the data that is about to be sent over the serial connection. For example:

    .. sourcecode:: python

        settings = SerialSettings.as_from('/dev/ttyS5:9600,8,1,N')
        printer = GenericESCPOS(settings.get_device())
        printer.init()
        1b 40                                            .@

        printer.text('Hello World!')
        48 65 6c 6c 6f 20 57 6f 72 6c 64 21              Hello World!
        0a                                               .

    """

    def write(self, data):
        if sys.stdout.isatty():
            sys.stdout.write(hexdump(data))
            sys.stdout.write(os.linesep)
        super(_SerialDumper, self).write(data)
