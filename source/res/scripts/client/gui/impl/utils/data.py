# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/utils/data.py
from __future__ import absolute_import
import typing
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
T = typing.TypeVar('T')

def findIndexes(arr, predicate):
    return [ idx for idx, item in enumerate(arr) if predicate(item) ]


def findItems(arr, predicate):
    return [ item for item in arr if predicate(item) ]
