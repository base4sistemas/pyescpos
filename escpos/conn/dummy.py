# -*- coding: utf-8 -*-
#
# escpos/conn/dummy.py
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


class DummyConnection(object):
    """Dummy printer.

    This class is used for saving commands to a variable, for use in situations
    where there is no need to send commands to an actual printer. This includes
    generating print jobs for later use, or testing output.
    """

    SETTINGS_EXAMPLE = None


    @classmethod
    def create(cls, settings):
        return cls()


    def __init__(self, *args, **kwargs):
        super(DummyConnection, self).__init__()
        self._output_list = []


    def write(self, data):
        """Print any command sent in raw format.

        :param str data: Arbitrary code to be printed.
        """
        self._output_list.append(data)


    @property
    def output(self):
        """Get the data that was sent to this printer."""
        return b''.join(self._output_list)


    def close(self):
        pass


    def catch(self):
        pass


    def read(self):
        pass
