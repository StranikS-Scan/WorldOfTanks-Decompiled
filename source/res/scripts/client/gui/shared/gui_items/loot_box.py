# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/loot_box.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.gui_item import GUIItem
from gui.shared.money import Currency
from shared_utils import CONST_CONTAINER

class NewYearLootBoxes(CONST_CONTAINER):
    PREMIUM = 'newYear_premium'
    COMMON = 'newYear_usual'


class NewYearCategories(CONST_CONTAINER):
    NEWYEAR = 'NewYear'
    CHRISTMAS = 'Christmas'
    ORIENTAL = 'Oriental'
    FAIRYTALE = 'Fairytale'


class EventCategories(CONST_CONTAINER):
    EVENT = 'Event'


class EventLootBoxes(CONST_CONTAINER):
    WT_HUNTER = 'wt_hunter'
    WT_BOSS = 'wt_boss'
    WT_SPECIAL = 'wt_special'


SENIORITY_AWARDS_LOOT_BOXES_TYPE = 'seniorityAwards'
GUI_ORDER = (EventLootBoxes.WT_HUNTER, EventLootBoxes.WT_BOSS, EventLootBoxes.WT_SPECIAL)
CATEGORIES_GUI_ORDER = (NewYearCategories.NEWYEAR,
 NewYearCategories.CHRISTMAS,
 NewYearCategories.ORIENTAL,
 NewYearCategories.FAIRYTALE,
 EventCategories.EVENT)

class LootBox(GUIItem):
    __slots__ = ('__id', '__invCount', '__type', '__category', '__isReroll', '__rerollSettings')

    def __init__(self, lootBoxID, lootBoxType, lootBoxCategory, invCount, reRoll=None):
        super(LootBox, self).__init__()
        self.__id = lootBoxID
        self.__invCount = invCount
        self.__type = lootBoxType
        self.__category = lootBoxCategory
        self.__isReroll = False if not reRoll else True
        self.__rerollSettings = reRoll if reRoll else {}

    def __repr__(self):
        return 'LootBox(id=%d, type=%s, category=%s, count=%d, isReroll=%s, rerollAttempts=%s)' % (self.getID(),
         self.getType(),
         self.getCategory(),
         self.getInventoryCount(),
         self.isReroll(),
         self.getReRollCount())

    def __cmp__(self, other):
        return cmp(self.getID(), other.getID())

    def updateCount(self, invCount):
        self.__invCount = invCount

    def update(self, lootBoxType, lootBoxCategory):
        self.__type = lootBoxType
        self.__category = lootBoxCategory

    def getInventoryCount(self):
        return self.__invCount

    def getID(self):
        return self.__id

    def getUserName(self):
        return backport.text(R.strings.lootboxes.type.dyn(self.__type)())

    def getType(self):
        return self.__type

    def getCategory(self):
        return self.__category

    def isFree(self):
        return self.__type == NewYearLootBoxes.COMMON

    def isEvent(self):
        return self.__category == EventCategories.EVENT

    def isReroll(self):
        return self.__isReroll

    def getReRollCount(self):
        return self.__rerollSettings.get('maxAttempts', 0)

    def getReRollPrice(self, reRolledAttempts=0):
        priceType = self.__rerollSettings.get('priceType', Currency.CREDITS)
        if reRolledAttempts > 0:
            reRolledAttempts -= 1
        if priceType == 'gold':
            priceType = Currency.GOLD
        reRollPrice = 0
        reRollPrices = self.__rerollSettings.get('prices', ())
        reRollPricesLen = len(reRollPrices)
        if 0 <= reRolledAttempts <= reRollPricesLen:
            reRollPrice = reRollPrices[reRolledAttempts]
        return (priceType, reRollPrice)
