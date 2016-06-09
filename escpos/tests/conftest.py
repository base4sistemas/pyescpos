# -*- coding: utf-8 -*-
#
# escpos/tests/conftest.py
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

class FakeDevice(object):
    """
    A fake device for testing printer implementations.
    """

    def __init__(self):
        super(FakeDevice, self).__init__()
        self._write_buffer = []
        self._read_buffer = ''


    @property
    def write_buffer(self):
        # write buffer is emptied once read
        content = ''.join(self._write_buffer)
        self._write_buffer[:] = []
        return content


    @property
    def read_buffer(self):
        # read buffer is emptied once read
        content = self._read_buffer
        self._read_buffer = ''
        return content


    @read_buffer.setter
    def read_buffer(self, value):
        self._read_buffer = value


    def catch(self):
        pass


    def write(self, data):
        self._write_buffer.extend(list(data))


    def read(self):
        return self.read_buffer


def pytest_namespace():
    return {'FakeDevice': FakeDevice}
