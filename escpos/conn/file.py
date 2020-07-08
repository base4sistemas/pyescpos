# -*- coding: utf-8 -*-
#
# escpos/conn/file.py
#
# Copyright 2017 KMEE INFORMATICA LTDA
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

import logging

from future.utils import python_2_unicode_compatible

from ..helpers import hexdump


logger = logging.getLogger('escpos.conn.file')


@python_2_unicode_compatible
class FileConnection(object):

    SETTINGS_EXAMPLE = '/dev/usb/lp0'

    @classmethod
    def create(cls, settings, **kwargs):
        return cls(devfile=settings, **kwargs)

    def __init__(self, devfile='/dev/usb/lp0', auto_flush=True):
        super(FileConnection, self).__init__()
        self.devfile = devfile
        self.auto_flush = auto_flush
        self.open()

    def __repr__(self):
        content = '{}(devfile={!r}, auto_flush={!r})'.format(
                self.__class__.__name__,
                self.devfile,
                self.auto_flush
            )
        return content

    def __str__(self):
        return self.devfile

    def open(self):
        """Open system file."""
        self.device = open(self.devfile, "wb")
        if self.device is None:
            print("Could not open the specified file {0}".format(self.devfile))

    def flush(self):
        """Flush printing content."""
        self.device.flush()

    def write(self, data):
        """Print any command sent in raw format.

        :param bytes data: arbitrary code to be printed.
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('writing to file %s:\n%s', self, hexdump(data))
        self.device.write(data)
        if self.auto_flush:
            self.flush()

    def close(self):
        """Close system file."""
        if self.device is not None:
            self.device.flush()
            self.device.close()

    def catch(self):
        return True

    def read(self):
        return None
