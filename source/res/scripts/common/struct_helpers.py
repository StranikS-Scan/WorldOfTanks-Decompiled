# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/struct_helpers.py
from struct import unpack, pack

def unpackByte(char):
    return unpack('B', char)[0]


def packByte(code):
    return pack('B', code)
