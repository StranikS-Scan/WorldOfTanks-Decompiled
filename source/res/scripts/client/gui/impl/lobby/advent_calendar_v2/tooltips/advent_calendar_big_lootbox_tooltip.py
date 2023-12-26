# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/tooltips/advent_calendar_big_lootbox_tooltip.py
from collections import OrderedDict
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillStringsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.advent_calendar.tooltips.advent_calendar_big_lootbox_tooltip_model import AdventCalendarBigLootboxTooltipModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.tooltips.bonus_item_view_model import BonusItemViewModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.tooltips.loot_box_bonus_view_model import LootBoxBonusViewModel
from gui.impl.pub import ViewImpl
from gui.shared.advent_calendar_v2_consts import GUARANTEED_REWARD_GROUP_NAME
from helpers import dependency
from skeletons.gui.game_control import IAdventCalendarV2Controller
BONUS_TYPE_TO_ICON_NAME = {'guest_cat': 'guest_cat',
 'randomNy24Toy': 'randomNy24Toy',
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
 'nyRandomResource': 'nyRandomResource',
 'color_fir': 'N24_ChTree_Color_05'}
_PROBABILITY_GROUPS_ORDER = OrderedDict((('guaranteed', ('ny_amber', 'ny_iron', 'ny_emerald', 'ny_crystal', 'nyRandomResource')),
 ('currency', ('gold', 'credits', 'premium_plus')),
 ('ny_items', ('guest_cat', 'randomNy24Toy', 'color_fir')),
 ('high_tier_vehicles', ()),
 ('low_tier_vehicles', ()),
 ('customizations', ())))

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
    __adventCalendarV2Ctrl = dependency.descriptor(IAdventCalendarV2Controller)

    def __init__(self, *args):
        settings = ViewSettings(R.views.lobby.advent_calendar.tooltips.AdventCalendarBigLootBoxTooltip())
        settings.model = AdventCalendarBigLootboxTooltipModel()
        settings.args = args
        super(AdventCalendarBigLootBoxTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdventCalendarBigLootBoxTooltip, self).getViewModel()

    def _onLoading(self, state, doorsToOpenAmount, isPostEvent, isShowStatus, *args, **kwargs):
        lootBoxInfo = self.__adventCalendarV2Ctrl.getLootBoxInfo()
        if lootBoxInfo:
            with self.viewModel.transaction() as tx:
                tx.setState(state)
                tx.setIsPostEvent(isPostEvent)
                tx.setDoorsToOpenAmount(doorsToOpenAmount)
                tx.setIsShowStatus(isShowStatus)
                self.__fillViewModel(tx, lootBoxInfo)
            super(AdventCalendarBigLootBoxTooltip, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return ((self.__adventCalendarV2Ctrl.onLootBoxInfoUpdated, self.__updateModel),)

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

    def __updateModel(self):
        lootBoxInfo = self.__adventCalendarV2Ctrl.getLootBoxInfo()
        if lootBoxInfo:
            with self.viewModel.transaction() as tx:
                self.__fillViewModel(tx, lootBoxInfo)
