# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/views/winback_selectable_reward_view.py
from collections import OrderedDict
from copy import deepcopy
from logging import getLogger
import typing
from AccountCommands import RES_SUCCESS
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus, WindowFlags, WindowLayer
from gui import GUI_NATIONS, GUI_NATIONS_ORDER_INDEX
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.common.fade_manager import useDefaultFade
from gui.impl.gen import R
from gui.impl.lobby.battle_matters.popovers.battle_matters_filter_popover_view import BattleMattersFilterPopoverView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.bonuses import VehiclesBonus
from gui.shared import g_eventBus
from gui.shared.missions.packers.bonus import packMissionsBonusModelAndTooltipData, BonusUIPacker
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, getNationLessName
from helpers import dependency
from nations import NONE_INDEX
from shared_utils import first
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.shared import IItemsCache
from winback.gui.impl.gen.view_models.views.lobby.views.winback_reward_view_model import RewardName
from winback.gui.impl.gen.view_models.views.lobby.views.winback_selectable_reward_view_model import WinbackSelectableRewardViewModel
from winback.gui.impl.lobby.tooltips.selectable_reward_tooltip import SelectableRewardTooltip
from winback.gui.impl.lobby.tooltips.selected_rewards_tooltip import SelectedRewardsTooltip
from winback.gui.impl.lobby.views.winback_bonus_packer import handleWinbackDiscounts, handleVehicleBonuses, cutVehDiscountsFromBonuses, getWinbackBonusPacker, WinbackBlueprintUIPacker, WINBACK_DISCOUNTS, WinbackDiscountBonusUIPacker
from winback.gui.impl.lobby.winback_helpers import SelectableTypes
from winback.gui.selectable_reward.selectable_reward_manager import WinbackSelectableRewardManager
from winback.gui.shared.event_dispatcher import showAwardsView
from winback.gui.shared.events import WinbackViewEvent
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.common.bonus_model import BonusModel
    from gui.SystemMessages import ResultMsg
    from winback.gui.impl.gen.view_models.views.lobby.views.selectable_reward_category_model import SelectableRewardCategoryModel
_NATIONS_KEY_NAME = 'Nations'
_TYPES_KEY_NAME = 'Types'
_logger = getLogger(__name__)

def getBonusPacker():
    packer = getWinbackBonusPacker()
    discountPacker = WinbackDiscountBonusUIPacker()
    packer.getPackers().update({'blueprints': WinbackBlueprintUIPacker(),
     RewardName.VEHICLE_FOR_GIFT.value: discountPacker,
     RewardName.VEHICLE_DISCOUNT.value: discountPacker,
     RewardName.VEHICLE_FOR_RENT.value: discountPacker})
    return packer


_TYPES_ORDER = ('heavyTank',
 'mediumTank',
 'lightTank',
 'AT-SPG',
 'SPG')

def _sortByNation(vehicleTuple):
    _, vehicleDict = vehicleTuple
    nation = vehicleDict['vehicle'].nationName
    return GUI_NATIONS_ORDER_INDEX.get(nation, NONE_INDEX)


def _sortByType(vehicleTuple):
    _, vehicleDict = vehicleTuple
    vehicleType = vehicleDict['vehicle'].type
    return _TYPES_ORDER.index(vehicleType)


def _sortByName(firstVehicleTuple, secondVehicleTuple):
    _, firstVehicleDict = firstVehicleTuple
    _, secondVehicleDict = secondVehicleTuple
    firstUserName = firstVehicleDict['vehicle'].userName
    secondUserName = secondVehicleDict['vehicle'].userName
    return cmp(firstUserName, secondUserName)


def _sortAndClearVehicles(vehicles):
    vehicleSortedByNations = sorted((vehItem for vehItem in vehicles if vehItem is not None), key=_sortByNation)
    sortedVehicles = []
    for nation in GUI_NATIONS:
        sortedByType = sorted([ (cd, veh) for cd, veh in vehicleSortedByNations if veh['vehicle'].nationName == nation ], key=_sortByType)
        finallySortedByType = []
        for vehicleType in _TYPES_ORDER:
            sortedByName = sorted([ (cd, veh) for cd, veh in sortedByType if veh['vehicle'].type == vehicleType ], cmp=_sortByName)
            finallySortedByType += sortedByName

        sortedVehicles += finallySortedByType

    return sortedVehicles


def _showRewardView(result):
    if result and result.auxData and result.auxData.get(RES_SUCCESS):
        showAwardsView(ctx={'quests': (),
         'bonuses': deepcopy(result.auxData[RES_SUCCESS]),
         'isOnlyDaily': False,
         'selectedRewards': True,
         'isLastWindow': False})


class WinbackSelectableRewardView(ViewImpl):
    __slots__ = ('__bonuses', '__filterPopover', '__filters', '__tooltipData', '__selectedTab')
    _selectableRewardManager = WinbackSelectableRewardManager
    _itemsCache = dependency.descriptor(IItemsCache)
    _winbackController = dependency.descriptor(IWinbackController)
    _packer = getBonusPacker()

    def __init__(self, selectableTokens=None):
        settings = ViewSettings(R.views.winback.lobby.WinbackSelectableRewardView())
        settings.flags = ViewFlags.VIEW
        settings.model = WinbackSelectableRewardViewModel()
        self.__bonuses = OrderedDict()
        self.__filterPopover = None
        self.__filters = {}
        self.__resetFilters(True)
        self.__tooltipData = {}
        self._update(selectableTokens)
        super(WinbackSelectableRewardView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(WinbackSelectableRewardView, self).getViewModel()

    def createPopOverContent(self, event):
        if event.contentID == R.views.lobby.battle_matters.popovers.BattleMattersFilterPopoverView():
            self.__filterPopover = BattleMattersFilterPopoverView(self.__filters, self.onUpdateFilter)
            return self.__filterPopover
        return super(WinbackSelectableRewardView, self).createPopOverContent(event)

    def createToolTip(self, event):
        tooltipId = event.getArgument('tooltipId')
        window = None
        if tooltipId is not None:
            tooltipData = self.__tooltipData.get(tooltipId)
            if tooltipData and isinstance(tooltipData, TooltipData):
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
        else:
            window = super(WinbackSelectableRewardView, self).createToolTip(event)
        return window

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.winback.lobby.tooltips.SelectedRewardsTooltip():
            return SelectedRewardsTooltip(self.__getSelectedRewards())
        if contentID == R.views.winback.lobby.tooltips.SelectableRewardTooltip():
            level = int(event.getArgument(WinbackSelectableRewardViewModel.VEHICLE_LEVEL))
            return SelectableRewardTooltip(**self.__bonuses[level]['tooltipData'].specialArgs)
        return super(WinbackSelectableRewardView, self).createToolTipContent(event, contentID)

    def onUpdateFilter(self, filters=None):
        if filters:
            self.__filters = filters
        self.__updateRewards()

    def onTabChange(self, event):
        newTab = int(event.get(WinbackSelectableRewardViewModel.VEHICLE_LEVEL))
        self.__selectTab(newTab)

    def onFilterReset(self):
        self.__resetFilters()

    def onSelectReward(self, event):
        eventIdx = int(event.get(WinbackSelectableRewardViewModel.REWARD_INDEX))
        model = self.viewModel.getSelectableRewards()[eventIdx]
        if self.__bonuses[self.__selectedTab]['isCompensation']:
            selectName = model.getIcon()
        else:
            selectName = model.getVehicleName()
        if self._deselect(selectName):
            self._select(eventIdx, selectName)
        self._updateTotalValues()

    def onClaimRewards(self):
        selectedRewards = self.__getSelectedRewards()
        rewardsToChoose = [ (self.__bonuses[tabName]['selectableBonus'], [reward['id']]) for tabName, reward in selectedRewards.iteritems() ]
        g_eventBus.addListener(WinbackViewEvent.WINBACK_REWARD_VIEW_LOADED, self.__onRewardViewLoaded)
        self._selectableRewardManager.chooseRewards(rewardsToChoose, _showRewardView)

    @useDefaultFade(layer=WindowLayer.SERVICE_LAYOUT)
    def __onRewardViewLoaded(self, _):
        self.destroyWindow()

    def _update(self, selectableTokens):
        if not self._winbackController.winbackConfig.isEnabled or not self._winbackController.isProgressionEnabled:
            return
        else:
            selectableBonuses = self._selectableRewardManager.getAvailableSelectableBonuses(None if selectableTokens is None else (lambda tID: tID in selectableTokens))
            for bonus in selectableBonuses:
                self.__bonuses[bonus.getLevel()] = self._createTabBonuses(bonus)

            self.__bonuses = OrderedDict(sorted(self.__bonuses.iteritems(), key=lambda item: item[0]))
            return

    def _createTabBonuses(self, bonus):
        currentTabBonuses = {}
        bonusType = bonus.getType()
        raw = deepcopy(self._selectableRewardManager.getRawBonusOptions(bonus))
        result = [ self.__createVehicleItem(giftId, opt, *self.__getOption(bonusType, opt)) for giftId, opt in raw.iteritems() ]
        currentTabBonuses['bonuses'] = OrderedDict(_sortAndClearVehicles(result))
        currentTabBonuses['isDiscount'] = bonus.isDiscount
        currentTabBonuses['isCompensation'] = bonusType == SelectableTypes.BLUEPRINTS
        currentTabBonuses['selectableBonus'] = bonus
        currentTabBonuses['tooltipData'] = first(bonus.getTooltip())
        return currentTabBonuses

    def _onLoading(self, *args, **kwargs):
        super(WinbackSelectableRewardView, self)._onLoading()
        self.__update()

    def _finalize(self):
        self.__filters = None
        self.__bonuses = None
        g_eventBus.removeListener(WinbackViewEvent.WINBACK_REWARD_VIEW_LOADED, self.__onRewardViewLoaded)
        super(WinbackSelectableRewardView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.destroyWindow),
         (self.viewModel.onCategorySelect, self.onTabChange),
         (self.viewModel.onFilterReset, self.onFilterReset),
         (self.viewModel.onSelectReward, self.onSelectReward),
         (self.viewModel.onConfirm, self.onClaimRewards),
         (g_playerEvents.onDisconnected, self.destroyWindow))

    def _deselect(self, selectedName):
        isCompensation = self.__bonuses[self.__selectedTab]['isCompensation']
        deselectName = None
        for reward in self.viewModel.getSelectableRewards():
            if reward.getIsSelected():
                if isCompensation:
                    deselectName = reward.getIcon()
                else:
                    deselectName = reward.getVehicleName()
                reward.setIsSelected(False)

        if deselectName is not None:
            self.__bonuses[self.__selectedTab]['bonuses'][deselectName]['isSelected'] = False
        else:
            for reward in self.__bonuses[self.__selectedTab]['bonuses'].itervalues():
                reward['isSelected'] = False

        return False if selectedName == deselectName else True

    def _select(self, eventIdx, selectedName):
        self.__bonuses[self.__selectedTab]['bonuses'][selectedName]['isSelected'] = True
        self.viewModel.getSelectableRewards()[eventIdx].setIsSelected(True)
        self._updateTotalValues()

    def _updateTotalValues(self):
        selectedRewardsCount = 0
        with self.viewModel.getCategories().transaction() as tabs:
            for tab in tabs:
                count = self.__getSelectedCount(int(tab.getVehicleLevel()))
                selectedRewardsCount += count
                tab.setIsSelected(tab.getVehicleLevel() == self.__selectedTab)
                tab.setRewardsSelected(count)

        self.viewModel.setTotalRewardsCount(len(self.__bonuses[self.__selectedTab]['bonuses']))
        self.viewModel.setSelectedRewardsCount(selectedRewardsCount)

    def __getSelectedRewards(self):
        return OrderedDict(sorted([ (tabName, reward) for tabName, tabContent in self.__bonuses.iteritems() for reward in tabContent['bonuses'].itervalues() if reward['isSelected'] ], key=lambda item: item[0]))

    def __getOption(self, bonusType, opt):
        intCD = -1
        option = None
        vehicle = None
        if bonusType == SelectableTypes.DISCOUNT:
            _, winbackDiscounts = cutVehDiscountsFromBonuses(opt['option'])
            winbackData = winbackDiscounts[WINBACK_DISCOUNTS]
            intCD = first(winbackData)
            vehicle = self._itemsCache.items.getItemByCD(intCD)
            baseCount, _ = self._itemsCache.items.blueprints.getBlueprintCount(intCD, vehicle.level)
            winbackData[intCD][BlueprintBonusTypes.BLUEPRINTS][intCD] += baseCount
            option = first(handleWinbackDiscounts(winbackDiscounts))
        elif bonusType == SelectableTypes.VEHICLE:
            if 'slots' in opt['option']:
                cd = first(opt['option'][VehiclesBonus.VEHICLES_BONUS])
                opt['option'][VehiclesBonus.VEHICLES_BONUS][cd]['slot'] = opt['option'].pop('slots')
            option = first(handleVehicleBonuses(opt['option']))
            intCD = first(option.getVehicleCDs())
            vehicle = self._itemsCache.items.getItemByCD(intCD)
        name = getNationLessName(vehicle.name)
        return (name,
         intCD,
         vehicle,
         option)

    def __selectTab(self, tabName):
        self.__selectedTab = tabName
        self.__updateRewards()
        self._updateTotalValues()

    def __update(self):
        with self.viewModel.transaction() as tx:
            tx.setProgressionName(self._winbackController.progressionName)
            with tx.getCategories().transaction() as tabs:
                tabs.clear()
                for tabLevel, tabContent in self.__bonuses.iteritems():
                    newTab = tx.getCategoriesType()()
                    newTab.setVehicleLevel(int(tabLevel))
                    newTab.setIsDiscount(tabContent['isDiscount'])
                    newTab.setIsCompensation(tabContent['isCompensation'])
                    newTab.setRewardsSelected(0)
                    newTab.setIsSelected(False)
                    tabs.addViewModel(newTab)

                if tabs:
                    self.__selectTab(int(tabs[0].getVehicleLevel()))

    def __updateRewards(self):
        with self.viewModel.transaction() as tx:
            with tx.getSelectableRewards().transaction() as rewards:
                needToApplyFilter = not self.__bonuses[self.__selectedTab]['isCompensation']
                isNationsFilterEmpty = self.__isFilterEmpty(_NATIONS_KEY_NAME)
                isTypesFilterEmpty = self.__isFilterEmpty(_TYPES_KEY_NAME)

                def __isMatchFilter(veh):
                    return isNationsFilterEmpty and isTypesFilterEmpty or isTypesFilterEmpty and self.__nationFit(veh) or isNationsFilterEmpty and self.__typeFit(veh) or self.__nationFit(veh) and self.__typeFit(veh)

                bonuses = self.__bonuses[self.__selectedTab]['bonuses']
                rewards.clear()
                options = [ giftData['option'] for giftData in bonuses.itervalues() if needToApplyFilter and __isMatchFilter(giftData['vehicle']) or not needToApplyFilter ]
                selectedIdx, selectedName = self.__getSelected(bonuses, options)
                self.__tooltipData = {}
                packMissionsBonusModelAndTooltipData(options, self._packer, rewards, self.__tooltipData)
        if selectedName is not None:
            self._select(selectedIdx, selectedName)
        return

    @staticmethod
    def __getSelected(bonuses, options):
        for bonusName, bonus in bonuses.iteritems():
            if bonus['isSelected']:
                try:
                    selectedIdx = options.index(bonus['option'])
                    selectedName = bonusName
                    return (selectedIdx, selectedName)
                except ValueError:
                    return (-1, None)

        return (-1, None)

    def __getSelectedCount(self, tabName):
        return sum((gift['isSelected'] for gift in self.__bonuses[tabName]['bonuses'].itervalues()))

    @staticmethod
    def __createBlueprintItem(giftId, gift):
        return (gift['option'].getImageCategory(), {'id': giftId,
          'option': gift['option'],
          'count': gift['count'],
          'limit': gift['limit'],
          'isSelected': False})

    def __createVehicleItem(self, giftId, opt, name, intCD, vehicle, option):
        inventoryVehicles = self._itemsCache.items.inventory.getIventoryVehiclesCDs()
        return None if intCD in inventoryVehicles else (name, {'id': giftId,
          'vehCD': intCD,
          'option': option,
          'vehicle': vehicle,
          'limit': opt['limit'],
          'count': opt['count'],
          'isSelected': False})

    def __isFilterEmpty(self, key):
        return not any((value for value in self.__filters[key].itervalues()))

    def __nationFit(self, veh):
        return self.__filters[_NATIONS_KEY_NAME][veh.nationName]

    def __typeFit(self, veh):
        return self.__filters[_TYPES_KEY_NAME][veh.type]

    def __resetFilters(self, init=False):
        self.__filters = {_NATIONS_KEY_NAME: OrderedDict(((nation, False) for nation in GUI_NATIONS)),
         _TYPES_KEY_NAME: OrderedDict(((t, False) for t in VEHICLE_TYPES_ORDER))}
        if self.__filterPopover and self.__filterPopover.viewStatus == ViewStatus.LOADED:
            self.__filterPopover.updateFilterFromOutside(self.__filters)
        elif not init:
            self.onUpdateFilter()


class WinbackSelectableRewardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, selectableTokens=None, parent=None):
        super(WinbackSelectableRewardWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackSelectableRewardView(selectableTokens), parent=parent)
