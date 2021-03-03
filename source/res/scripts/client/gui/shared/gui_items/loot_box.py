# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/loot_box.py
import typing
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


BLACK_MARKET_ITEM_TYPE = 'blackMarket'
SENIORITY_AWARDS_LOOT_BOXES_TYPE = 'seniorityAwards'
GUI_ORDER = (NewYearLootBoxes.COMMON, NewYearLootBoxes.PREMIUM)
CATEGORIES_GUI_ORDER = (NewYearCategories.NEWYEAR,
 NewYearCategories.CHRISTMAS,
 NewYearCategories.ORIENTAL,
 NewYearCategories.FAIRYTALE)

class LootBox(GUIItem):
    __slots__ = ('__id', '__invCount', '__type', '__category', '__historyName', '__guaranteedFrequency', '__guaranteedFrequencyName', '__rerollSettings', '__autoOpenTime', '__isReroll', '__bonus')

    def __init__(self, lootBoxID, lootBoxConfig, invCount):
        super(LootBox, self).__init__()
        self.__id = lootBoxID
        self.__invCount = invCount
        self.__updateByConfig(lootBoxConfig)

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

    def update(self, lootBoxConfig):
        self.__updateByConfig(lootBoxConfig)

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

    def getAutoOpenTime(self):
        return self.__autoOpenTime

    def getReRollPrice(self, reRolledAttempts=0):
        priceType = self.__rerollSettings.get('priceType', Currency.CREDITS)
        if reRolledAttempts > 0:
            reRolledAttempts -= 1
        if priceType == 'gold':
            priceType = Currency.GOLD
        reRollPrice = 0
        reRollPrices = self.__rerollSettings.get('prices', ())
        reRollPricesLen = len(reRollPrices)
        if 0 <= reRolledAttempts < reRollPricesLen:
            reRollPrice = reRollPrices[reRolledAttempts]
        return (priceType, reRollPrice)

    def getBonusVehicles(self):
        vehs = []
        for bonusesGroup in self.__bonus.get('groups'):
            for bonuses in bonusesGroup.get('oneof'):
                if bonuses:
                    for bonus in bonuses:
                        vehs += [ veh for veh in bonus[3].get('vehicles', {}).keys() ]

        return vehs

    def getGuaranteedFrequency(self):
        return self.__guaranteedFrequency

    def getGuaranteedFrequencyName(self):
        return self.__guaranteedFrequencyName

    def getHistoryName(self):
        return self.__historyName

    def __updateByConfig(self, lootBoxConfig):
        self.__type = lootBoxConfig.get('type')
        self.__category = lootBoxConfig.get('category')
        self.__historyName = lootBoxConfig.get('historyName')
        self.__rerollSettings = lootBoxConfig.get('reRoll')
        self.__bonus = lootBoxConfig.get('bonus')
        self.__autoOpenTime = lootBoxConfig.get('autoOpenTime')
        self.__isReroll = True if self.__rerollSettings else False
        self.__guaranteedFrequencyName, self.__guaranteedFrequency = self.__readLimits(lootBoxConfig.get('limits', {}))

    @staticmethod
    def __readLimits(limitsCfg):
        for limitName, limit in limitsCfg.iteritems():
            if 'useBonusProbabilityAfter' in limit:
                return (limitName, limit['useBonusProbabilityAfter'] + 1)

        return (None, 0)
