# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/anonymizer_shared.py
import struct
import zlib

def getUsersListCheckSum(usersList):
    if len(usersList) == 0:
        return 0
    sortedList = sorted(list(usersList))
    return zlib.crc32(' '.join(sortedList))
