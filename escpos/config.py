# -*- coding: utf-8 -*-
#
# escpos/config.py
#
# Copyright 2018 Base4 Sistemas Ltda ME
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

import os

from .constants import BACKOFF_DEFAULT_MAXTRIES
from .constants import BACKOFF_DEFAULT_DELAY
from .constants import BACKOFF_DEFAULT_FACTOR

try:
    from decouple import config as decouple_config
    _lib_decouple = True
except ImportError:
    _lib_decouple = False


def _env(var_name, default):
    if _lib_decouple:
        return decouple_config(var_name, cast=int, default=default)
    else:
        value = os.getenv(var_name)
        return default if value is None else int(value)


BACKOFF_MAXTRIES = _env('ESCPOS_BACKOFF_MAXTRIES', BACKOFF_DEFAULT_MAXTRIES)
BACKOFF_DELAY = _env('ESCPOS_BACKOFF_DELAY', BACKOFF_DEFAULT_DELAY)
BACKOFF_FACTOR = _env('ESCPOS_BACKOFF_FACTOR', BACKOFF_DEFAULT_FACTOR)
