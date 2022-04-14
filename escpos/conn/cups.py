# -*- coding: utf-8 -*-
#
# escpos/conn/cups.py
#
# Copyright 2022 KMEE LTDA
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
import tempfile
import subprocess

from .file import FileConnection

from future.utils import python_2_unicode_compatible

from ..helpers import hexdump

from tempfile import NamedTemporaryFile


logger = logging.getLogger('escpos.conn.file')


@python_2_unicode_compatible
class CupsConnection(FileConnection):

    @classmethod
    def create(cls, setting, **kwargs):
        """Instantiate a :class:`NetworkConnection` (or subclass) object based
        on a given host name and port number (eg. ``192.168.0.205:9100``).
        """
        cups_ip, printer_name = setting.rsplit(',', 1)
        return cls(cups_ip, printer_name, **kwargs)

    def __init__(self, cups_ip, printer_name, **kwargs):
        self.temp_file = NamedTemporaryFile()
        super(CupsConnection, self).__init__(devfile=self.temp_file.name, **kwargs)
        self.cups_ip = cups_ip
        self.printer_name = printer_name

    def open(self):
        """Open system file."""
        self.device = open(self.devfile, "wb+")
        if self.device is None:
            print("Could not open the specified file {0}".format(self.devfile))

    def write(self, data):
        """Print any command sent in raw format.
        :param bytes data: arbitrary code to be printed by cups.
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('writing to file %s:\n%s', self, hexdump(data))
        self.device.write(data)
        if self.auto_flush:
            self.flush()

    def close(self):
        """Close system file."""
        super(CupsConnection, self).close()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('sends to printer %s with cups %s:\n%s', self.printer_name, self.cups_ip, hexdump(data))
        print_process = subprocess.Popen(
            ['lp', '-h', self.cups_ip, '-d', self.printer_name, self.devfile],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print_process.wait(timeout=3000)
        self.temp_file.close()
