# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/item_info.py
from gui.impl.gen import R
from helpers import dependency
from items import festival
from items.components.festival_constants import FEST_TYPE_IDS, FEST_ITEM_TYPE, FEST_ITEM_QUALITY
from skeletons.festival import IFestivalController
from skeletons.gui.shared import IItemsCache

class FestivalItemInfo(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__descriptor',)

    def __init__(self, itemID):
        self.__descriptor = festival.g_cache.getFestivalItem(itemID)

    def __cmp__(self, other):
        return FEST_ITEM_TYPE.ALL.index(self.getType()) - FEST_ITEM_TYPE.ALL.index(other.getType())

    def getID(self):
        return self.__descriptor.getID()

    def getResId(self):
        basis = self.__festController.getGlobalPlayerCard().getBasis()
        altResId = basis.getAltResIds().get(self.getID())
        return self.__descriptor.getResId() if altResId is None else altResId

    def getAltResIds(self):
        return self.__descriptor.getAltResIds()

    def getDefaultResId(self):
        return self.__descriptor.getResId()

    def getType(self):
        return self.__descriptor.getType()

    def getQuality(self):
        return self.__descriptor.getQuality()

    def getCost(self):
        return self.__descriptor.getCost()

    def isAllowedToBuy(self):
        return self.__descriptor.isAllowedToBuy()

    def getWeight(self):
        return self.__descriptor.getWeight()

    def isAlternative(self):
        if self.getType() == FEST_ITEM_TYPE.BASIS:
            return bool(self.getAltResIds())
        else:
            magicBasis = self.__festController.getMagicBasis()
            return magicBasis is not None and magicBasis.isInInventory() and self.getID() in magicBasis.getAltResIds()

    def isSpecial(self):
        return self.getQuality() == FEST_ITEM_QUALITY.SPECIAL

    def isInInventory(self):
        itemsBytes = self.__itemsCache.items.festivity.getItemsBytes()
        return festival.hasFestivalItem(self.getID(), itemsBytes)

    def isSeen(self):
        seenItemsBytes = self.__itemsCache.items.festivity.getSeenItemsBytes()
        return festival.hasFestivalItem(self.getID(), seenItemsBytes)

    def isInPlayerCard(self):
        cardInd = FEST_TYPE_IDS[self.getType()]
        return self.getID() == self.__itemsCache.items.festivity.getPlayerCard()[cardInd]

    def getNameResID(self):
        return R.strings.festival_items.dyn('id_' + str(self.getID())).name()

    def getDescription(self):
        return R.strings.festival_items.dyn('id_' + str(self.getID())).dyn('desc')

    def getLockedTextResID(self):
        return R.strings.festival_items.dyn('id_' + str(self.getID())).locked()

    def getTypeResID(self):
        return R.strings.festival_items.type.dyn(self.getType())()

    def getIconResID(self, useDefault=False):
        resId = self.getDefaultResId() if useDefault else self.getResId()
        return R.images.gui.maps.icons.festival.items.big.dyn(self.getType()).dyn(resId)()

    def getSmallIconResID(self):
        return R.images.gui.maps.icons.festival.items.small.dyn(self.getType()).dyn(self.getResId())()

    @staticmethod
    def getBasisResID():
        return R.images.gui.maps.icons.festival.items.big.dyn(FEST_ITEM_TYPE.BASIS).default()
