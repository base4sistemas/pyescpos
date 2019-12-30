# -*- coding: utf-8 -*-
#
# escpos/impl/__init__.py
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

import six

from . import bematech  # noqa: F401
from . import daruma  # noqa: F401
from . import elgin  # noqa: F401
from . import epson  # noqa: F401
from . import nitere  # noqa: F401
from . import unknown  # noqa: F401


__all__ = [
        'bematech',
        'daruma',
        'elgin',
        'epson',
        'nitere',
        'unknown',
    ]

if six.PY2:
    __all__ = [name.encode('latin-1') for name in __all__]
