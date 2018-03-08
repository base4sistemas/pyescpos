# -*- coding: utf-8 -*-
#
# escpos/feature.py
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

from collections import namedtuple

"""A bunch of identifiers representing hardware features."""

COLUMNS = 'columns'
CUTTER = 'cutter'
CASHDRAWER_PORTS = 'cashdrawer-ports'
CASHDRAWER_AVAILABLE_PORTS = 'cashdrawer-available-ports'
PORTABLE = 'portable'


Columns = namedtuple('Columns', 'normal expanded condensed')


class FeatureAttributes(object):

    def __init__(self, impl):
        self._impl = impl

    def __getattr__(self, attr):
        if attr in self._impl.hardware_features:
            return self._impl.hardware_features[attr]
        raise AttributeError('\'{}.feature\' object has no attribute {!r}'.format(
                self._impl.__class__.__name__, attr))


_SET = {
        COLUMNS: Columns(normal=48, expanded=24, condensed=64),
        CUTTER: False,
        CASHDRAWER_PORTS: True,
        CASHDRAWER_AVAILABLE_PORTS: 2,
        PORTABLE: False,
    }
"""Default features set."""
