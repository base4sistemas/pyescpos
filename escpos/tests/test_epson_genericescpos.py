# -*- coding: utf-8 -*-
#
# escpos/tests/test_epson_genericescpos.py
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

import pytest

from escpos.impl.epson import GenericESCPOS
from escpos import feature


@pytest.fixture(scope='module')
def printer():
    return GenericESCPOS(pytest.FakeDevice())


def test_has_model_attr(printer):
    assert hasattr(printer, 'model')


def test_has_feature_attribute(printer):
    assert hasattr(printer, 'feature')
    assert isinstance(printer.feature, feature.FeatureAttributes)


def test_feature_attribute_columns(printer):
    assert hasattr(printer.feature, feature.COLUMNS)
    assert printer.feature.columns.normal == 48
    assert printer.feature.columns.expanded == 24
    assert printer.feature.columns.condensed == 64

