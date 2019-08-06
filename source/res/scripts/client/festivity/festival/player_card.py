# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/player_card.py
from festivity.festival.item_info import FestivalItemInfo
from items.components.festival_constants import FEST_ITEM_TYPE

class PlayerCard(object):
    __slots__ = ('__playerCard',)

    def __init__(self, playerCard):
        self.__playerCard = {}
        self.update(playerCard)

    def getBasis(self):
        return self.__playerCard[FEST_ITEM_TYPE.BASIS]

    def getEmblem(self):
        return self.__playerCard[FEST_ITEM_TYPE.EMBLEM]

    def getTitle(self):
        return self.__playerCard[FEST_ITEM_TYPE.TITLE]

    def getRank(self):
        return self.__playerCard[FEST_ITEM_TYPE.RANK]

    def getItemIDByType(self, typeName):
        return self.__playerCard[typeName]

    def getRawData(self):
        result = []
        for itemType in FEST_ITEM_TYPE.ALL:
            result.append(self.__playerCard[itemType].getID())

        return result

    def setItem(self, itemID):
        festItem = FestivalItemInfo(itemID)
        self.__playerCard[festItem.getType()] = festItem

    def update(self, playerCard):
        for ind, itemType in enumerate(FEST_ITEM_TYPE.ALL):
            self.__playerCard[itemType] = FestivalItemInfo(playerCard[ind])
