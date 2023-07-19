# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/loot_box.py
from enum import Enum
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.gui_item import GUIItem
from shared_utils import CONST_CONTAINER

class NewYearLootBoxes(CONST_CONTAINER):
    PREMIUM = 'newYear_premium'
    SPECIAL = 'newYear_special'
    SPECIAL_AUTO = 'newYear_special_auto'
    COMMON = 'newYear_usual'


class NewYearCategories(CONST_CONTAINER):
    NEWYEAR = 'NewYear'
    CHRISTMAS = 'Christmas'
    ORIENTAL = 'Oriental'
    FAIRYTALE = 'Fairytale'


class EventCategories(CONST_CONTAINER):
    EVENT = 'Event'


class WTLootBoxes(CONST_CONTAINER):
    WT_HUNTER = 'wt_hunter'
    WT_BOSS = 'wt_boss'
    WT_SPECIAL = 'wt_special'


class LunarNYLootBoxTypes(Enum):
    BASE = 'lunar_base'
    SIMPLE = 'lunar_simple'
    SPECIAL = 'lunar_special'


class EventLootBoxes(CONST_CONTAINER):
    PREMIUM = 'event_premium'
    COMMON = 'event_common'


ALL_LUNAR_NY_LOOT_BOX_TYPES = ('lunar_base', 'lunar_simple', 'lunar_special')
LUNAR_NY_LOOT_BOXES_CATEGORIES = 'LunarNY'
SENIORITY_AWARDS_LOOT_BOXES_TYPE = 'seniorityAwards'
EVENT_LOOT_BOXES_CATEGORY = 'eventLootBoxes'
GUI_ORDER_NY = (NewYearLootBoxes.COMMON, NewYearLootBoxes.PREMIUM)
CATEGORIES_GUI_ORDER_NY = (NewYearCategories.NEWYEAR,
 NewYearCategories.CHRISTMAS,
 NewYearCategories.ORIENTAL,
 NewYearCategories.FAIRYTALE)

class LootBox(GUIItem):
    __slots__ = ('__id', '__invCount', '__type', '__category', '__historyName', '__guaranteedFrequency', '__guaranteedFrequencyName')

    def __init__(self, lootBoxID, lootBoxConfig, invCount):
        super(LootBox, self).__init__()
        self.__id = lootBoxID
        self.__invCount = invCount
        self.__updateByConfig(lootBoxConfig)

    def __repr__(self):
        return 'LootBox(id=%d, type=%s, category=%s, count=%d)' % (self.getID(),
         self.getType(),
         self.getCategory(),
         self.getInventoryCount())

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
        self.__guaranteedFrequencyName, self.__guaranteedFrequency = self.__readLimits(lootBoxConfig.get('limits', {}))

    @staticmethod
    def __readLimits(limitsCfg):
        for limitName, limit in limitsCfg.iteritems():
            if 'useBonusProbabilityAfter' in limit:
                return (limitName, limit['useBonusProbabilityAfter'] + 1)

        return (None, 0)
