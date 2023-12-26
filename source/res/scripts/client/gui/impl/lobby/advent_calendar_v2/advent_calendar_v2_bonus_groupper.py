# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/advent_calendar_v2_bonus_groupper.py
from enum import Enum
from gui.goodies.goodie_items import Booster
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_helper import getFlattenedBonuses
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache

class QuestRewardsGroups(Enum):
    CURRENCIES_AND_PREMIUM = 'currenciesAndPremium'
    BOOSTERS = 'boosters'
    CUSTOMIZATIONS = 'customizations'
    CREW_BONUSES_OR_X5 = 'crewBonusesOrX5'
    PROGRESSION_REWARDS = 'progressionRewards'
    EXPERIMENTAL_EQUIPMENT_AND_COMPONENTS = 'experimentalEquipmentAndComponents'


class AdventCalendarV2QuestsBonusGrouper(object):
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, groupAndValueExtractorMapping=None):
        self.excluded = ('battleTokens',)
        self._groupAndValueExtractors = {'goodies': self._extractGoodies,
         'credits': self._extractCurrency,
         'tokens': self._extractTokens,
         'crewBooks': self._extractCrewBook,
         'premium_plus': self._extractCurrency,
         'customizations': self._extrcatCustomizations,
         'crewSkins': self._extractCrewSkins,
         'equipCoin': self._extractCurrency,
         'items': self._extractItems}
        if groupAndValueExtractorMapping is not None:
            self._groupAndValueExtractors.update(groupAndValueExtractorMapping)
        return

    @staticmethod
    def _extractCurrency(bonus):
        name = bonus.getName()
        if name == 'equipCoin':
            return {QuestRewardsGroups.EXPERIMENTAL_EQUIPMENT_AND_COMPONENTS: {name}}
        if name == 'premium_plus':
            name = 'premium_plus_universal'
        return {QuestRewardsGroups.CURRENCIES_AND_PREMIUM: {name}}

    @staticmethod
    def _extractTokens(bonus):
        return {QuestRewardsGroups.CREW_BONUSES_OR_X5: {'bonus_battle_task'}} if 'battle_bonus_x5' in bonus.getValue() else {}

    @staticmethod
    def _extractCrewBook(_):
        return {QuestRewardsGroups.CREW_BONUSES_OR_X5: {'brochure_random'}}

    @staticmethod
    def _extrcatCustomizations(bonus):
        values = set()
        for v in bonus.getValue():
            custType = v['custType']
            if custType == 'projection_decal':
                custType = 'projectionDecal'
            values.add(custType)

        return {QuestRewardsGroups.CUSTOMIZATIONS: values}

    @staticmethod
    def _extractCrewSkins(_):
        return {QuestRewardsGroups.CUSTOMIZATIONS: {'crewSkin1'}}

    @staticmethod
    def _emptyExtractor(_):
        return {}

    @staticmethod
    def _extractGoodies(bonus):
        grouppedBonuses = {}
        for goodieId in bonus.getValue():
            goodie = AdventCalendarV2QuestsBonusGrouper.__goodiesCache.getGoodie(goodieId)
            if isinstance(goodie, Booster):
                grouppedBonuses.setdefault(QuestRewardsGroups.BOOSTERS, set()).add(goodie.boosterGuiType)
            grouppedBonuses.setdefault(QuestRewardsGroups.CREW_BONUSES_OR_X5, set()).add(goodie.itemTypeName)

        return grouppedBonuses

    @staticmethod
    def _extractItems(bonus):
        for item in bonus.getItems():
            if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isModernized:
                return {QuestRewardsGroups.EXPERIMENTAL_EQUIPMENT_AND_COMPONENTS: {'expequipments_gift'}}

        return {}

    def group(self, quests):
        grouppedBonuses = {}
        for bonus in getFlattenedBonuses(quests):
            name = bonus.getName()
            for group, value in self._groupAndValueExtractors.get(name, self._emptyExtractor)(bonus).items():
                grouppedBonuses.setdefault(group, set()).update(value)

        return grouppedBonuses
