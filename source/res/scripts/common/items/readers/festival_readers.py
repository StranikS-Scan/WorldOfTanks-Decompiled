# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/festival_readers.py
import typing
import ResMgr
import contextlib
from items.components.festival_components import FestivalItemDescriptor, ProgressRewardDescriptor
from soft_exception import SoftException

@contextlib.contextmanager
def openSection(path):
    try:
        yield ResMgr.openSection(path)
    finally:
        ResMgr.purge(path)


def readFestivalItem(xmlPath):
    cache = {}
    with openSection(xmlPath) as section:
        if section is None:
            raise SoftException("Can't open '%s'" % xmlPath)
        for itemSec in section.values():
            item = FestivalItemDescriptor.createItemBySection(itemSec)
            if item.getID() in cache:
                raise SoftException("Repeated itemID - '%s'" % item.getID())
            cache[item.getID()] = item

    return cache


def readFestivalProgressRewards(xmlPath):
    cache = []
    with openSection(xmlPath) as section:
        if section is None:
            raise SoftException("Can't open '%s'" % xmlPath)
        for itemSec in section.values():
            item = ProgressRewardDescriptor.createItemBySection(itemSec)
            cache.append(item)

    return cache
