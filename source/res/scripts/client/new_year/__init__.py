# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/__init__.py
import typing
if typing.TYPE_CHECKING:
    from typing import Optional

def parseHangarNameMask(mask):
    if mask is None:
        return (0, 0)
    else:
        titleIdx = mask & 65535
        descriptionIdx = mask >> 16 & 65535
        return (titleIdx, descriptionIdx)


def makeHangarNameMask(titleIdx, descriptionIdx):
    return (descriptionIdx << 16) + titleIdx
