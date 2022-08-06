# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/core/common.py
import typing
from enum import Enum
from itertools import izip_longest
from helpers import getClientVersion

def getClientBuildVersion():
    return getClientVersion(force=False)


def grouper(iterable, batch):
    args = [iter(iterable)] * batch
    for parts in izip_longest(fillvalue=None, *args):
        yield [ part for part in parts if part is not None ]

    return


def convertEnum(value):
    return value.value if isinstance(value, Enum) else value
