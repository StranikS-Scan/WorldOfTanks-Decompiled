# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/loot_box.py
from __future__ import absolute_import
from enum import Enum
from future.utils import iteritems
from past.builtins import cmp
from typing import TYPE_CHECKING
from gui.impl import backport
from gui.impl.gen import R
from gui.lootbox_system.base.common import getTextResource
from gui.shared.gui_items.gui_item import GUIItem
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Dict, Optional, Tuple

class NewYearLootBoxes(CONST_CONTAINER):
    PREMIUM = 'newYear_premium'


class WTLootBoxes(CONST_CONTAINER):
    WT_HUNTER = 'wt_hunter'
    WT_BOSS = 'wt_boss'
    WT_SPECIAL = 'wt_special'


class LunarNYLootBoxTypes(Enum):
    BASE = 'lunar_base'
    SIMPLE = 'lunar_simple'
    SPECIAL = 'lunar_special'


ALL_LUNAR_NY_LOOT_BOX_TYPES = ('lunar_base', 'lunar_simple', 'lunar_special')
LUNAR_NY_LOOT_BOXES_CATEGORIES = 'LunarNY'
SENIORITY_AWARDS_LOOT_BOXES_TYPE = 'seniorityAwards'

class LootBox(GUIItem):
    __slots__ = ('__id', '__invCount', '__isEnabled', '__type', '__category', '__bonus', '__historyName', '__statsName', '__guaranteedFrequency', '__guaranteedFrequencyName', '__probabilityBonusName', '__probabilityBonusLimit', '__rerollCurrency', '__rerollPrices', '__rerollMaxAttempts', '__bonuses')
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
        if self.__type in self.__lootBoxSystem.eventNames:
            name = getTextResource(['common', 'boxCategory', 'lowerCase'] + [self.__category], self.__type)
            return backport.text(name() if name.exists() else R.strings.lootbox_system.common.boxCategory.lowerCase.default())
        return backport.text(R.strings.lootboxes.type.dyn(self.__type)())

    def getType(self):
        return self.__type

    def getCategory(self):
        return self.__category

    def isFree(self):
        return self.__type != NewYearLootBoxes.PREMIUM

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

    def getRerollCurrency(self):
        return self.__rerollCurrency

    def getRerollPrices(self):
        return self.__rerollPrices

    def getRerollMaxAttempts(self):
        return self.__rerollMaxAttempts

    def isRerollable(self):
        return self.__rerollMaxAttempts is not None

    def _compare(self, other):
        return cmp(self.getID(), other.getID())

    def getBonuses(self):
        return self.__bonuses

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
        self.__rerollCurrency, self.__rerollPrices, self.__rerollMaxAttempts = self.__readRerolls(lootBoxConfig.get('reroll'))
        self.__bonuses = lootBoxConfig.get('bonus', {})

    @staticmethod
    def __readProbabilityBonusLimit(limitsCfg):
        for probabilityBonusName, limit in iteritems(limitsCfg):
            if 'useBonusProbabilityAfter' in limit:
                return (probabilityBonusName, limit['useBonusProbabilityAfter'] + 1)
            if 'guaranteedFrequency' in limit:
                return (probabilityBonusName, limit['guaranteedFrequency'])

        return (None, 0)

    @staticmethod
    def __readFrequencyLimit(limitsCfg):
        for limitName, limit in iteritems(limitsCfg):
            if 'guaranteedFrequency' in limit:
                return (limitName, limit['guaranteedFrequency'])

        return (None, 0)

    @staticmethod
    def __readRerolls(rerollCfg):
        return (None, None, None) if rerollCfg is None else (rerollCfg['currency'], tuple(rerollCfg['prices']), rerollCfg['maxAttempts'])
