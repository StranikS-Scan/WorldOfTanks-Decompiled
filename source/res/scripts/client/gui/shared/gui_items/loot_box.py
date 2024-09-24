# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/loot_box.py
from enum import Enum
from typing import TYPE_CHECKING
from gui.impl import backport
from gui.impl.gen import R
from gui.lootbox_system.common import getTextResource
from gui.shared.gui_items.gui_item import GUIItem
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Dict, Optional

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
    __slots__ = ('__id', '__invCount', '__isEnabled', '__type', '__category', '__bonus', '__historyName', '__statsName', '__guaranteedFrequency', '__guaranteedFrequencyName', '__probabilityBonusName', '__probabilityBonusLimit')
    __lootBoxSystem = dependency.descriptor(ILootBoxSystemController)

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

    def isEnabled(self):
        return self.__isEnabled

    def getID(self):
        return self.__id

    def getUserName(self):
        if self.__lootBoxSystem.isEnabled and self.__lootBoxSystem.eventName == self.__type:
            name = getTextResource('common/boxCategory/lowerCase'.split('/') + [self.__category])
            return backport.text(name() if name.exists() else R.strings.lootbox_system.common.boxCategory.lowerCase.default())
        return backport.text(R.strings.lootboxes.type.dyn(self.__type)())

    def getType(self):
        return self.__type

    def getCategory(self):
        return self.__category

    def isFree(self):
        return self.__type == NewYearLootBoxes.COMMON

    def getBonusInfo(self):
        return self.__bonus

    def getGuaranteedFrequency(self):
        return self.__guaranteedFrequency

    def getGuaranteedFrequencyName(self):
        return self.__guaranteedFrequencyName

    def getProbabilityBonusLimit(self):
        return self.__probabilityBonusLimit

    def getProbabilityBonusLimitName(self):
        return self.__probabilityBonusName

    def getHistoryName(self):
        return self.__historyName

    def getStatsName(self):
        return self.__statsName

    def getUseStats(self):
        return bool(self.__statsName)

    def __updateByConfig(self, lootBoxConfig):
        self.__isEnabled = lootBoxConfig.get('enabled')
        self.__type = lootBoxConfig.get('type')
        self.__category = lootBoxConfig.get('category')
        self.__bonus = lootBoxConfig.get('bonus', {})
        self.__statsName = lootBoxConfig.get('statsInfo', '')
        self.__historyName = lootBoxConfig.get('historyName')
        limitsConfig = lootBoxConfig.get('limits', {})
        self.__guaranteedFrequencyName, self.__guaranteedFrequency = self.__readFrequencyLimit(limitsConfig)
        self.__probabilityBonusName, self.__probabilityBonusLimit = self.__readProbabilityBonusLimit(limitsConfig)

    @staticmethod
    def __readProbabilityBonusLimit(limitsCfg):
        for probabilityBonusName, limit in limitsCfg.iteritems():
            if 'useBonusProbabilityAfter' in limit:
                return (probabilityBonusName, limit['useBonusProbabilityAfter'] + 1)

        return (None, 0)

    @staticmethod
    def __readFrequencyLimit(limitsCfg):
        for limitName, limit in limitsCfg.iteritems():
            if 'guaranteedFrequency' in limit:
                return (limitName, limit['guaranteedFrequency'])

        return (None, 0)
