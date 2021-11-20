# -*- coding: utf-8 -*-
#
# escpos/helpers.py
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

import inspect
import time

from collections import namedtuple
from itertools import takewhile
from operator import attrgetter

from builtins import chr
from builtins import bytes

import six
from six.moves import zip_longest

from .exceptions import TimeoutException


_Model = namedtuple('_Model', 'name vendor')

Implementation = namedtuple('Implementation', 'model type fqname')


def find_implementations(sort_by=None):
    """
    Returns a tuple of :class:`~escpos.helpers.Implementation` objects
    containing metadata for all known implementations (subclasses of
    :class:`~escpos.impl.epson.GenericESCPOS`) with vendor and model names, the
    implementation type and its fully qualified name.

    This example will print all vendor and model names, sorted by vendor name:

    .. sourcecode::

        for impl in find_implementations(sort_by='model.vendor'):
            print impl.model.vendor, ':', impl.model.name

    :param str sort_by: Attribute name to sort the resulting list (optional).

    :rtype: tuple

    """
    impls = [_describe_impl(t) for t in _list_impls()]
    if sort_by:
        impls.sort(key=attrgetter(sort_by))
    return tuple(impls)


class TimeoutHelper(object):

    def __init__(self, timeout=1):
        self._timeout = timeout
        self.set()

    @property
    def timeout(self):
        return self._timeout

    def set(self):
        self._mark = time.time()

    def check(self):
        if self.timeout > 0:
            if time.time() - self._mark > self.timeout:
                raise TimeoutException((
                        '{!r} seconds have passed'
                    ).format(self.timeout))
        return False


class ByteValue(object):
    """A helper for easy bit handling."""

    def __init__(self):
        self._int_value = 0

    @property
    def byte(self):
        return six.int2byte(self._int_value)

    @property
    def value(self):
        return self._int_value

    def get_bit(self, n):
        return ((self._int_value >> n & 1) != 0)

    def set_bit(self, n):
        self._int_value |= (1 << n)

    def clear_bit(self, n):
        self._int_value &= ~(1 << n)


def chunks(iterable, size):
    def grouper(n, iterable, fillvalue=None):
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    for chunk in grouper(size, iterable):
        data = [i for i in takewhile(lambda e: e is not None, chunk)]
        yield bytearray(data)


def to_bytes(content, encoding='utf-8', errors='strict'):
    """Convert a sequence to a bytes type.

    Borrowed from `PySerial <https://github.com/pyserial/pyserial>`_ since
    it is now optional.
    """
    if isinstance(content, bytes):
        # Python 2: isinstance('', bytes) is True
        return bytes(content)
    elif isinstance(content, bytearray):
        return bytes(content)
    elif isinstance(content, memoryview):
        return content.tobytes()
    elif isinstance(content, six.string_types):
        return bytes(content.encode(encoding, errors))
    else:
        # handle list of integers and bytes (one or more items)
        # for Python 2 and 3
        return bytes(bytearray(content))


def hexdump(content, encoding='utf-8', errors='strict', eol='\n', panel_gap=2):
    b_content = to_bytes(content, encoding=encoding, errors=errors)
    hex_panel, char_panel = hexdump_bytes(b_content)
    gap = ' ' * panel_gap
    return eol.join(
            '{}{}{}'.format(h, gap, c)
            for h, c in zip(hex_panel, char_panel)
        )


def hexdump_bytes(data, fill_last_line=True):
    def _hex_values():
        return ['{:02x}'.format(b) for b in data]

    def _chr_values():
        return [chr(b) if 32 <= b <= 126 else '.' for b in data]

    def _cut(sequence, size):
        for i in range(0, len(sequence), size):
            yield sequence[i:i + size]

    hex_panel = [' '.join(line) for line in _cut(_hex_values(), 16)]
    char_panel = [''.join(line) for line in _cut(_chr_values(), 16)]

    if hex_panel and fill_last_line:
        hex_panel[-1] = hex_panel[-1] + (' ' * (47 - len(hex_panel[-1])))

    if char_panel and fill_last_line:
        char_panel[-1] = char_panel[-1] + (' ' * (16 - len(char_panel[-1])))

    return hex_panel, char_panel


def is_value_in(constants_group, value):
    """Checks whether value can be found in the given constants group,
    which in turn, must be a Django-like choices tuple.
    """
    return value in [k for k, v in constants_group]


def _list_impls():
    from escpos.impl.epson import GenericESCPOS
    return _impls_for(GenericESCPOS)


def _impls_for(t):
    impls = [t]
    for subcls in t.__subclasses__():
        impls.extend(_impls_for(subcls))
    return impls


def _describe_impl(t):
    impl = Implementation(
            model=_Model(name=t.model.name, vendor=t.model.vendor),
            type=t,
            fqname=_fqname(t)
        )
    return impl


def _fqname(t):
    m = inspect.getmodule(t)
    return '.'.join([m.__name__, t.__name__])
