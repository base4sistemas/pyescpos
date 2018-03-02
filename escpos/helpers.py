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

import inspect
import time

from collections import namedtuple
from operator import attrgetter

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
        self.timeout = 1
        self.set()


    def set(self):
        self._mark = time.time()


    def check(self):
        if self.timeout > 0:
            if time.time() - self._mark > self.timeout:
                raise TimeoutException('%s seconds have passed' % self.timeout)
        return False


def chunks(iterable, size):
    def chunk_factory(iterable, size):
        args = [iter(iterable)] * size
        return zip_longest(*args, fillvalue=None)
    for chunk in chunk_factory(iterable, size):
        yield ''.join([e for e in chunk if e is not None])
    raise StopIteration()


def hexdump(data):
    def _cut(sequence, size):
        for i in range(0, len(sequence), size):
            yield sequence[i:i+size]
    _hex = lambda seq: ['{0:02x}'.format(b) for b in seq]
    _chr = lambda seq: [chr(b) if 32 <= b <= 126 else '.' for b in seq]
    raw_data = map(ord, data)
    hexpanel = [' '.join(line) for line in _cut(_hex(raw_data), 16)]
    chrpanel = [''.join(line) for line in _cut(_chr(raw_data), 16)]
    hexpanel[-1] = hexpanel[-1] + (chr(32) * (47 - len(hexpanel[-1])))
    chrpanel[-1] = chrpanel[-1] + (chr(32) * (16 - len(chrpanel[-1])))
    return '\n'.join('%s  %s' % (h, c) for h, c in zip(hexpanel, chrpanel))


def is_value_in(constants_group, value):
    """
    Checks whether value can be found in the given constants group, which in
    turn, should be a Django-like choices tuple.
    """
    for const_value, label in constants_group:
        if const_value == value:
            return True
    return False


def _list_impls():
    from escpos.impl.epson import GenericESCPOS
    return _impls_for(GenericESCPOS)


def _impls_for(t):
    impls = [t,]
    for subcls in t.__subclasses__():
        impls.extend(_impls_for(subcls))
    return impls


def _describe_impl(t):
    impl = Implementation(
            model=_Model(name=t.model.name, vendor=t.model.vendor),
            type=t,
            fqname=_fqname(t))
    return impl


def _fqname(t):
    m = inspect.getmodule(t)
    return '.'.join([m.__name__, t.__name__])
