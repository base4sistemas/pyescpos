# -*- coding: utf-8 -*-
#
# pyescpos/conn/win32.py
#
# Copyright 2022 KMEE INFORMATICA LTDA
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


logger = logging.getLogger('pyescpos.conn.win32')


_WIN32PRINT = False
try:
    import win32print

    _WIN32PRINT = True
except ImportError:
    pass

if not _WIN32PRINT:

    class Win32Raw(object):
        def __init__(self, **kwargs):
            raise ImportError

else:

    class Win32Raw(object):
        def __init__(self, printer_name=None, *args, **kwargs):
            if printer_name is not None:
                self.printer_name = printer_name
            else:
                self.printer_name = win32print.GetDefaultPrinter()
            self.hPrinter = None
            self.open()

        @classmethod
        def create(cls, settings, **kwargs):
            return cls(printer_name=settings, **kwargs)

        def catch(self):
            pass

        def open(self, job_name="pyescpos"):
            if self.printer_name is None:
                raise Exception("Printer not found")
            self.hPrinter = win32print.OpenPrinter(self.printer_name)
            self.current_job = win32print.StartDocPrinter(
                self.hPrinter, 1, (job_name, None, "RAW")
            )
            win32print.StartPagePrinter(self.hPrinter)

        def close(self):
            if not self.hPrinter:
                return
            win32print.EndPagePrinter(self.hPrinter)
            win32print.EndDocPrinter(self.hPrinter)
            win32print.ClosePrinter(self.hPrinter)
            self.hPrinter = None

        def write(self, msg):
            """Print any command sent in raw format

            :param msg: arbitrary code to be printed
            :type msg: bytes
            """
            if self.printer_name is None:
                raise Exception("Printer not found")
            if self.hPrinter is None:
                raise Exception("Printer job not opened")
            win32print.WritePrinter(self.hPrinter, msg)

        def read(self):
            pass

