# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/talismans.py
from gui.impl.gen import R
from helpers import dependency
from items import new_year
from skeletons.gui.shared import IItemsCache

class TalismanItem(object):
    __slots__ = ('__descriptor',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemID):
        self.__descriptor = new_year.g_cache.talismans[itemID]

    def getID(self):
        return self.__descriptor.id

    def getSetting(self):
        return self.__descriptor.setting

    def isInInventory(self):
        return self.__descriptor.id in self._itemsCache.items.festivity.getTalismans()

    def getSmallIcon(self):
        return R.images.gui.maps.icons.new_year.talismans.small.dyn(self.getSetting())()

    def getBigIcon(self):
        return R.images.gui.maps.icons.new_year.talismans.big.dyn(self.getSetting())()
