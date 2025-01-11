# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/tooltips/advent_calendar_big_lootbox_tooltip.py
import logging
from collections import OrderedDict
from typing import Tuple
from advent_calendar.gui.feature.constants import GUARANTEED_REWARD_GROUP_NAME, ADVENT_CALENDAR_TOKEN
from advent_calendar.gui.impl.gen.view_models.views.lobby.tooltips.big_lootbox_tooltip_model import BigLootboxTooltipModel, ProgressionState
from advent_calendar.gui.impl.gen.view_models.views.lobby.tooltips.bonus_item_view_model import BonusItemViewModel
from advent_calendar.gui.impl.gen.view_models.views.lobby.tooltips.loot_box_bonus_view_model import LootBoxBonusViewModel
from advent_calendar.gui.impl.lobby.feature.advent_helper import getAccountTokensAmount, getQuestNeededTokensCount
from advent_calendar.skeletons import IAdventCalendarController
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillStringsArray
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
_logger = logging.getLogger(__name__)
BONUS_TYPE_TO_ICON_NAME = {'guest_cat': 'guest_cat',
 'randomNyToy': 'randomNyToy',
 'highTierVehicles': 'vehicles',
 'lowTierVehicles': 'vehicles',
 'gold': 'gold',
 'ny_amber': 'ny_amber',
 'ny_iron': 'ny_iron',
 'ny_emerald': 'ny_emerald',
 'ny_crystal': 'ny_crystal',
 'premium_plus': 'premium_plus_universal',
 'credits': 'credits',
 'style_3d': 'style_3d',
 'style_2d': 'style',
 'attachment': 'attachment',
 'nyRandomResource': 'nyRandomResource',
 'color_fir': 'N24_ChTree_Color_05'}
_PROBABILITY_GROUPS_ORDER = OrderedDict((('guaranteed', ('gold', 'ny_amber', 'ny_iron', 'ny_emerald', 'ny_crystal', 'nyRandomResource')),
 ('currency', ('gold', 'premium_plus', 'credits')),
 ('ny_items', ('guest_cat', 'randomNyToy', 'color_fir')),
 ('attachments', ()),
 ('customizations', ()),
 ('high_tier_vehicles', ()),
 ('low_tier_vehicles', ())))

def _sortGroups(bonusGroup):
    groupName = bonusGroup[0]
    return _PROBABILITY_GROUPS_ORDER.keys().index(groupName) if groupName in _PROBABILITY_GROUPS_ORDER else len(_PROBABILITY_GROUPS_ORDER)


def _sortBonuses(bonus, groupName):
    order = _PROBABILITY_GROUPS_ORDER.get(groupName, {})
    name = bonus[0]
    return order.index(name) if name in order else len(order)


def _sortUiValues(value, bonusType):
    return int(value) if bonusType in ('gold', 'credits', 'premium_plus') else value


def _adjustProbabilityForUi(probability):
    return round(100 * probability, 2)


class AdventCalendarBigLootBoxTooltip(ViewImpl):
    __adventController = dependency.descriptor(IAdventCalendarController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.advent_calendar.lobby.feature.tooltips.AdventCalendarBigLootBoxTooltip(), model=BigLootboxTooltipModel(), args=args, kwargs=kwargs)
        super(AdventCalendarBigLootBoxTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdventCalendarBigLootBoxTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self.__adventController.onLootBoxInfoUpdated, self.__onLootBoxInfoUpdated),)

    def _onLoading(self, questID=None, *args, **kwargs):
        lootBoxInfo = self.__adventController.getLootBoxInfo()
        if not lootBoxInfo:
            _logger.error('Lootbox info not found.')
            return
        else:
            state, doorsToOpenAmount = self.__getModelInfo(questID)
            with self.viewModel.transaction() as tx:
                tx.setIsShowStatus(questID is not None)
                tx.setState(state)
                tx.setIsPostEvent(self.__adventController.isInPostActivePhase())
                tx.setDoorsToOpenAmount(doorsToOpenAmount)
                self.__fillViewModel(tx, lootBoxInfo)
            super(AdventCalendarBigLootBoxTooltip, self)._onLoading(*args, **kwargs)
            return

    def __fillViewModel(self, viewModel, lootBoxInfo):
        viewModel.setBoxName(lootBoxInfo.name)
        viewModel.setBoxCategory(lootBoxInfo.category)
        modelBonuses = viewModel.getBonuses()
        modelBonuses.clear()
        for groupName, probabilityGroups in sorted(lootBoxInfo.bonuses.items(), key=_sortGroups):
            for probability, bonuses in sorted(probabilityGroups.items(), key=lambda x: x[0]):
                bonusModel = LootBoxBonusViewModel()
                bonusModel.setProbability(_adjustProbabilityForUi(probability))
                if groupName == GUARANTEED_REWARD_GROUP_NAME:
                    bonusModel.setIsGuaranteed(True)
                self.__fillBonusModelItems(bonusModel, groupName, bonuses)
                modelBonuses.addViewModel(bonusModel)

        modelBonuses.invalidate()

    @staticmethod
    def __fillBonusModelItems(bonusViewModel, groupName, bonuses):
        items = bonusViewModel.getBonusItems()
        items.clear()
        for bonusType, values in sorted(bonuses.items(), key=lambda b: _sortBonuses(b, groupName)):
            if bonusType in BONUS_TYPE_TO_ICON_NAME:
                itemModel = BonusItemViewModel()
                itemModel.setType(bonusType)
                itemModel.setIconName(BONUS_TYPE_TO_ICON_NAME[bonusType])
                valueModel = itemModel.getValue()
                valueModel.clear()
                fillStringsArray(sorted(values, key=lambda x: _sortUiValues(x, bonusType)), valueModel)
                items.addViewModel(itemModel)

        items.invalidate()

    def __onLootBoxInfoUpdated(self):
        lootBoxInfo = self.__adventController.getLootBoxInfo()
        if not lootBoxInfo:
            return
        with self.viewModel.transaction() as tx:
            self.__fillViewModel(tx, lootBoxInfo)

    def __getModelInfo(self, questID):
        if questID is None:
            return (ProgressionState.REWARD_RECEIVED, 0)
        else:
            prevQuest = None
            quest = None
            for q in self.__adventController.progressionRewardQuestsOrdered:
                if q.getID() == questID:
                    quest = q
                    break
                prevQuest = q

            if quest.isCompleted():
                return (ProgressionState.REWARD_RECEIVED, 0)
            if prevQuest is not None and not prevQuest.isCompleted():
                return (ProgressionState.REWARD_LOCKED, 0)
            accountTokensAmount = getAccountTokensAmount(ADVENT_CALENDAR_TOKEN)
            requiredTokensAmount = getQuestNeededTokensCount(quest)
            doorsToOpenAmount = requiredTokensAmount - accountTokensAmount
            return (ProgressionState.REWARD_IN_PROGRESS, doorsToOpenAmount)
