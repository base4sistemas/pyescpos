# -*- coding: utf-8 -*-
#
# escpos/constants.py
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

CASHDRAWER_DEFAULT_DURATION = 200
"""Duration for cash drawer activation (kick) in milliseconds.
See :meth:`~escpos.impl.epson.GenericESCPOS.kick_drawer` method for details.
"""

BACKOFF_DEFAULT_MAXTRIES = 3
"""Number of tries before give up. See :func:`escpos.retry.backoff`"""

BACKOFF_DEFAULT_DELAY = 3
"""Delay between retries (in seconds). See :func:`escpos.retry.backoff`"""

BACKOFF_DEFAULT_FACTOR = 2
"""Multiply factor in which delay will be increased for the next retry.
See :func:`escpos.retry.backoff`.
"""
