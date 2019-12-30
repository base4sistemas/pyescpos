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

from decouple import config

from .constants import BACKOFF_DEFAULT_MAXTRIES
from .constants import BACKOFF_DEFAULT_DELAY
from .constants import BACKOFF_DEFAULT_FACTOR


BACKOFF_MAXTRIES = config(
        'ESCPOS_BACKOFF_MAXTRIES',
        cast=int,
        default=BACKOFF_DEFAULT_MAXTRIES)

BACKOFF_DELAY = config(
        'ESCPOS_BACKOFF_DELAY',
        cast=int,
        default=BACKOFF_DEFAULT_DELAY)

BACKOFF_FACTOR = config(
        'ESCPOS_BACKOFF_FACTOR',
        cast=int,
        default=BACKOFF_DEFAULT_FACTOR)
