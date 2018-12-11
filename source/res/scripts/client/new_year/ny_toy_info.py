# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_toy_info.py
import random
from frameworks.wulf import Resource
from helpers import dependency
from items import collectibles
from gui.impl.gen import R
from items import ny19
from items.components.ny_constants import TOY_COLLECTION_BYTES
from new_year.ny_constants import TOY_PREFIX
from skeletons.gui.shared import IItemsCache
_PASSEPARTOUTS = ('passepartout_1', 'passepartout_2', 'passepartout_3', 'passepartout_4')
_EMPTY_PASSEPARTOUT = '_empty_passpartout'

class _NewYearCommonToyInfo(object):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_descriptor',)

    def __init__(self, descriptor):
        super(_NewYearCommonToyInfo, self).__init__()
        self._descriptor = descriptor

    def getToyType(self):
        return self._descriptor.type

    def getID(self):
        return self._descriptor.id

    def getSetting(self):
        return self._descriptor.setting

    def getRank(self):
        return int(self._descriptor.rank)

    def getIconName(self):
        return self._descriptor.icon


class NewYear18ToyInfo(_NewYearCommonToyInfo):
    __slots__ = ()

    def __init__(self, toyID):
        super(NewYear18ToyInfo, self).__init__(collectibles.g_cache.ny18.toys[toyID])

    def getName(self):
        return R.strings.toys18.dyn(self._descriptor.name)

    def getDesc(self):
        return R.strings.toys18.descr.dyn(self._descriptor.name)

    def getIcon(self):
        return R.images.gui.maps.icons.new_year.toys18.big.dyn(self._descriptor.icon)

    def isInCollection(self):
        toyCollection = self._itemsCache.items.festivity.getToyCollection()
        toyID = self.getID()
        bytePos = TOY_COLLECTION_BYTES + toyID / 8
        mask = 1 << toyID % 8
        return True if toyCollection[bytePos] & mask else False

    def getShards(self):
        return ny19.calculateOldCraftCost(self.getID())

    def getCollectionName(self):
        return self.getSetting()

    def getEmptyPassepartout(self):
        return R.images.gui.maps.icons.new_year.album.page18.passepartout_empty

    def getPassepartout(self):
        passepartout = random.choice(_PASSEPARTOUTS)
        return R.images.gui.maps.icons.new_year.album.page18.dyn(passepartout)


class NewYear19ToyInfo(_NewYearCommonToyInfo):
    __slots__ = ()

    def __init__(self, toyID):
        super(NewYear19ToyInfo, self).__init__(collectibles.g_cache.ny19.toys[toyID])

    def getLocalKey(self):
        return TOY_PREFIX + str(self.getID())

    def getName(self):
        return R.strings.ny.decorations.dyn(self.getLocalKey()).name

    def getDesc(self):
        return R.strings.ny.decorations.dyn(self.getLocalKey()).description if self.getRank() == 5 else Resource.INVALID

    def getShards(self):
        return ny19.getToyCost(toyDescr=self._descriptor)

    def getAtmosphere(self):
        return ny19.CONSTS.TOY_ATMOSPHERE_BY_RANK[self.getRank() - 1]

    def getToyObject(self):
        return ny19.getObjectByToyType(self.getToyType())

    def getCollectionName(self):
        return self.getSetting()

    def getIcon(self):
        return R.images.gui.maps.icons.new_year.toys19.big.dyn(self._descriptor.icon)

    def getEmptyPassepartout(self):
        return R.images.gui.maps.icons.new_year.album.page19.dyn(self.getToyType() + _EMPTY_PASSEPARTOUT)

    def getPassepartout(self):
        passepartout = random.choice(_PASSEPARTOUTS)
        return R.images.gui.maps.icons.new_year.album.page19.dyn(passepartout)

    def isInCollection(self):
        toyCollection = self._itemsCache.items.festivity.getToyCollection()
        toyID = self.getID()
        bytePos = toyID >> 3
        mask = 1 << toyID % 8
        return True if toyCollection[bytePos] & mask else False
