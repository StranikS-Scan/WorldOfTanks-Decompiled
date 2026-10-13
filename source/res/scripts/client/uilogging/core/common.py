# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/core/common.py
from __future__ import absolute_import
import typing
from enum import Enum
from future.moves.itertools import zip_longest
from helpers import getClientVersion

def getClientBuildVersion():
    return getClientVersion(force=False)


def grouper(iterable, batch):
    args = [iter(iterable)] * batch
    for parts in zip_longest(fillvalue=None, *args):
        yield [ part for part in parts if part is not None ]

    return


def convertEnum(value):
    if isinstance(value, Enum):
        return value.value
    return int(value) if hasattr(value, '__enum__') else value
