# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/bonus_grouper.py
from __future__ import absolute_import
from enum import Enum
from advent_calendar.gui.impl.lobby.feature.advent_helper import getFlattenedBonuses
from gui.goodies.goodie_items import Booster, DemountKit, RecertificationForm, MentoringLicense
from gui.server_events.bonuses import C11nProgressTokenBonus, splitBonuses
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


class AdventCalendarQuestsBonusGrouper(object):
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, groupAndValueExtractorMapping=None):
        self._groupAndValueExtractors = {'goodies': self._extractGoodies,
         'credits': self._extractCurrency,
         'tokens': self._extractTokens,
         'crewBooks': self._extractCrewBook,
         'premium_plus': self._extractCurrency,
         'customizations': self._extractCustomizations,
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
        return {QuestRewardsGroups.CREW_BONUSES_OR_X5: {'universal_brochure'}}

    @staticmethod
    def _extractCustomizations(bonus):
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
        groupedBonuses = {}
        for goodieId in bonus.getValue():
            goodie = AdventCalendarQuestsBonusGrouper.__goodiesCache.getGoodie(goodieId)
            if isinstance(goodie, Booster):
                groupedBonuses.setdefault(QuestRewardsGroups.BOOSTERS, set()).add(goodie.boosterGuiType)
            if isinstance(goodie, (DemountKit, RecertificationForm)):
                groupedBonuses.setdefault(QuestRewardsGroups.CREW_BONUSES_OR_X5, set()).add(goodie.itemTypeName)

        return groupedBonuses

    @staticmethod
    def _extractItems(bonus):
        for item in bonus.getItems():
            if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isModernized:
                return {QuestRewardsGroups.EXPERIMENTAL_EQUIPMENT_AND_COMPONENTS: {'expequipments_gift'}}

        return {}

    def group(self, quests):
        groupedBonuses = {}
        for bonus in getFlattenedBonuses(quests):
            name = bonus.getName()
            for group, value in self._groupAndValueExtractors.get(name, self._emptyExtractor)(bonus).items():
                groupedBonuses.setdefault(group, set()).update(value)

        return groupedBonuses


class RewardsBonusGroups(Enum):
    CREW_MEMBER = 'crewMember'
    LOOTBOX = 'lootbox'
    PREMIUM = 'premium_plus'
    STYLE_2D = 'style'
    DECAL = 'projection_decal'
    RESERVE_CREDITS = 'booster_credits'
    RESERVE_EXP = 'booster_xp'
    RESERVE_COMBINED_EXP = 'booster_free_xp_and_crew_xp'
    CREW_BONUSES = 'booklet'
    RECERTIFICATION_FORM = 'recertificationForm'
    MENTORING_LICENSE = 'mentoringLicense'
    BATTLE_BONUS_5X = 'battleBonus5X'
    EXPERIMENTAL_EQUIPMENT = 'experimental_equipment'
    CREDITS = 'credits'
    COMPONENTS = 'equipCoin'
    FREEXP = 'freeXP'
    NONE = 'none'


class RewardBonusGrouper(object):
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, groupAndValueExtractorMapping=None):
        self._groupAndValueExtractors = {'goodies': self._extractGoodies,
         'credits': self._extractCurrency,
         'tokens': self._extractTokens,
         'crewBooks': self._extractCrewBook,
         'premium_plus': self._extractCurrency,
         'customizations': self._extractCustomizations,
         'tmanToken': self._extractTman,
         'equipCoin': self._extractCurrency,
         'currencies': self._extractCurrencies,
         'items': self._extractItems,
         'lootBox': self._extractLootBoxes,
         'freeXP': self._extractCurrency,
         C11nProgressTokenBonus.BONUS_NAME: self._extractProgressionCustomizations}
        if groupAndValueExtractorMapping is not None:
            self._groupAndValueExtractors.update(groupAndValueExtractorMapping)
        return

    @staticmethod
    def _extractCurrency(bonus):
        try:
            return RewardsBonusGroups(bonus.getName())
        except ValueError:
            return

    @staticmethod
    def _extractLootBoxes(_):
        return RewardsBonusGroups.LOOTBOX

    @staticmethod
    def _extractCurrencies(bonus):
        try:
            return RewardsBonusGroups(bonus.getCode())
        except ValueError:
            return

    @staticmethod
    def _extractTokens(bonus):
        return RewardsBonusGroups.BATTLE_BONUS_5X if 'battle_bonus_x5' in bonus.getValue() else None

    @staticmethod
    def _extractCrewBook(_):
        return RewardsBonusGroups.CREW_BONUSES

    @staticmethod
    def _extractCustomizations(bonus):
        customizations = bonus.getValue()
        if not customizations:
            return
        try:
            return RewardsBonusGroups(customizations[0]['custType'])
        except ValueError:
            return

    @staticmethod
    def _extractProgressionCustomizations(_):
        return RewardsBonusGroups.STYLE_2D

    @staticmethod
    def _extractTman(_):
        return RewardsBonusGroups.CREW_MEMBER

    @staticmethod
    def _emptyExtractor(_):
        return None

    @classmethod
    def _extractGoodies(cls, bonus):
        goodieIds = bonus.getValue().keys()
        if not goodieIds:
            return
        try:
            goodie = cls.__goodiesCache.getGoodie(goodieIds[0])
            if isinstance(goodie, Booster):
                return RewardsBonusGroups(goodie.boosterGuiType)
            if isinstance(goodie, (DemountKit, RecertificationForm, MentoringLicense)):
                return RewardsBonusGroups(goodie.itemTypeName)
        except ValueError:
            return

    @staticmethod
    def _extractItems(bonus):
        for item in bonus.getItems():
            if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isModernized:
                return RewardsBonusGroups.EXPERIMENTAL_EQUIPMENT

    def group(self, bonuses):
        groupedBonuses = []
        for bonus in splitBonuses(bonuses):
            group = self._groupAndValueExtractors.get(bonus.getName(), self._emptyExtractor)(bonus)
            if group:
                groupedBonuses.append((group, bonus))

        return groupedBonuses
