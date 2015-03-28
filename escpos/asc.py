# -*- coding: utf-8 -*-
#
# escpos/asc.py
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

NUL = 0
SOH = 1
STX = 2
ETX = 3
EOT = 4
ENQ = 5
ACK = 6
BEL = 7
BS = 8
HT = 9
LF = 10
VT = 11
FF = 12
CR = 13
SO = 14
SI = 15
DLE = 16
DC1 = 17
DC2 = 18
DC3 = 19
DC4 = 20
NAK = 21
SYN = 22
ETB = 23
CAN = 24
EM = 25
SUB = 26
ESC = 27
FS = 28
GS = 29
RS = 30
US = 31

MNEMONIC_TABLE = (
        (NUL, 'NUL'),
        (SOH, 'SOH'),
        (STX, 'STX'),
        (ETX, 'ETX'),
        (EOT, 'EOT'),
        (ENQ, 'ENQ'),
        (ACK, 'ACK'),
        (BEL, 'BEL'),
        (BS, 'BS'),
        (HT, 'HT'),
        (LF, 'LF'),
        (VT, 'VT'),
        (FF, 'FF'),
        (CR, 'CR'),
        (SO, 'SO'),
        (SI, 'SI'),
        (DLE, 'DLE'),
        (DC1, 'DC1'),
        (DC2, 'DC2'),
        (DC3, 'DC3'),
        (DC4, 'DC4'),
        (NAK, 'NAK'),
        (SYN, 'SYN'),
        (ETB, 'ETB'),
        (CAN, 'CAN'),
        (EM, 'EM'),
        (SUB, 'SUB'),
        (ESC, 'ESC'),
        (FS, 'FS'),
        (GS, 'GS'),
        (RS, 'RS'),
        (US, 'US'),)


def mnemonic(n):
    """
    Returns mnemonic for ``n`` if ``0 <= n <= 31`` or ``None``.
    """
    if 0 <= n <= 31:
        return MNEMONIC_TABLE[n][1]
    return None


def value(mnemonic):
    """
    Returns the value of mnemonic (case-insensitive). Raises ``ValueError`` if
    the given mnemonic does not exists.
    """
    codes, mnemonics = zip(*MNEMONIC_TABLE)
    return mnemonics.index(mnemonic.upper())
