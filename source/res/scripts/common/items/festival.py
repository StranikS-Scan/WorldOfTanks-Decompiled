# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/festival.py
from collections import defaultdict
import typing
from items.components.festival_components import FestivalItemDescriptor
from items.components.festival_components import ProgressRewardDescriptor
from items.components.festival_constants import COLLECTION_XML_PATH, PROGRESS_REWARDS_XML_PATH, FEST_ITEM_TYPE, FEST_ITEM_QUALITY
from items.readers.festival_readers import readFestivalItem, readFestivalProgressRewards
g_cache = None

class FestivalCache(object):
    __slots__ = ('__collection', '__progressRewards', '__commonItems')

    def __init__(self):
        self.__collection = {}
        self.__progressRewards = []
        self.__commonItems = defaultdict(set)
        self.init()

    def getCollection(self):
        return self.__collection

    def getFestivalItem(self, itemID):
        return self.__collection[itemID]

    def getProgressRewards(self):
        return self.__progressRewards

    def getCommonItems(self, randomName):
        return self.__commonItems[randomName]

    def init(self):
        self.__collection = readFestivalItem(COLLECTION_XML_PATH)
        self.__progressRewards = readFestivalProgressRewards(PROGRESS_REWARDS_XML_PATH)
        for item in self.__collection.itervalues():
            if item.getQuality() == FEST_ITEM_QUALITY.COMMON:
                self.__commonItems[item.getType()].add(item.getID())

        anyCommonItems = set()
        for randomSet in self.__commonItems.itervalues():
            anyCommonItems.update(randomSet)

        self.__commonItems[FEST_ITEM_TYPE.ANY] = anyCommonItems

    def fini(self):
        self.__collection.clear()
        self.__commonItems.clear()
        self.__progressRewards = []


def init():
    global g_cache
    if g_cache is None:
        g_cache = FestivalCache()
    return


def hasFestivalItem(itemID, festivalItems):
    bytePos = itemID / 8
    mask = 1 << itemID % 8
    return bool(festivalItems[bytePos] & mask) if bytePos < len(festivalItems) else False


def setFestivalItem(itemID, festivalItems):
    bytePos = itemID / 8
    mask = 1 << itemID % 8
    if bytePos >= len(festivalItems):
        size = len(festivalItems)
        festivalItems.extend([0] * (bytePos - size + 1))
    festivalItems[bytePos] |= mask


def delFestivalItem(itemID, festivalItems):
    bytePos = itemID / 8
    mask = 1 << itemID % 8
    if bytePos < len(festivalItems):
        festivalItems[bytePos] &= ~mask


def countFestivalItems(festivalItems):
    return sum((hasFestivalItem(itemID, festivalItems) and isNecessaryToCount(itemID) for itemID in g_cache.getCollection()))


def isNecessaryToCount(festivalItemID):
    festItem = g_cache.getFestivalItem(festivalItemID)
    return festItem.getQuality() != FEST_ITEM_QUALITY.SPECIAL and festItem.getType() != FEST_ITEM_TYPE.RANK


def _getPlayerCardInd(itemID):
    festItem = g_cache.getFestivalItem(itemID)
    return festItem.getTypeID()


def hasItemInPlayerCard(itemID, playerCard):
    cardInd = _getPlayerCardInd(itemID)
    return playerCard[cardInd] == itemID


def setItemInPlayerCard(itemID, playerCard):
    cardInd = _getPlayerCardInd(itemID)
    playerCard[cardInd] = itemID


def canBuyOneMorePacks(mask):
    canBuyPacks = 0
    for randomName in FEST_ITEM_TYPE.ALL:
        for itemID in g_cache.getCommonItems(randomName):
            if not hasFestivalItem(itemID, mask):
                canBuyPacks += 1
                break

    return True if canBuyPacks > 1 else False


def getRandomCost(randomName, inventoryMask, priceConfig):
    if randomName != FEST_ITEM_TYPE.ANY and canBuyOneMorePacks(inventoryMask):
        return (priceConfig[randomName]['cost'], randomName)
    else:
        return (priceConfig[FEST_ITEM_TYPE.ANY]['cost'], FEST_ITEM_TYPE.ANY)


def commonCollectionIsAcquired(inventoryMask):
    return all((hasFestivalItem(itemID, inventoryMask) for itemID in g_cache.getCommonItems(FEST_ITEM_TYPE.ANY)))
