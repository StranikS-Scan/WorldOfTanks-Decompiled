# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/vehicle_selection_view.py
from collections import OrderedDict
import typing
from new_year.gui.impl.gen.view_models.views.lobby.new_year.vehicle_selection_models.selectable_reward_category_model import SelectableRewardCategoryModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.vehicle_selection_models.selectable_reward_view_model import SelectableRewardViewModel
from new_year.gui.impl.lobby.new_year.popovers.vehicle_filter_popover import VehicleFilterPopover
from new_year.gui.impl.new_year.tooltips.ny_discount_reward_tooltip import NyDiscountRewardTooltip
from new_year.gui.impl.new_year.tooltips.ny_selected_rewards_tooltip import SelectedRewardsTooltip
from new_year.gui.shared.gui_items.processors.ny_processor import ApplyVehicleDiscountProcessor
from new_year.gui.shared.variadic_discount import VariadicDiscount
from new_year.helpers.ny_helpers import _getVariadicID
from new_year_common.items.components.ny_constants import TOKEN_VARIADIC_DISCOUNT_PREFIX
from frameworks.wulf import ViewSettings
from frameworks.wulf import ViewStatus
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui import GUI_NATIONS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.utils.decorators import adisp_process
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from typing import Tuple, Sequence, Callable, Optional
    from Event import Event
_NATIONS_KEY_NAME = 'Nations'
_TYPES_KEY_NAME = 'Types'
_TYPES_ORDER = ('heavyTank', 'mediumTank', 'lightTank', 'AT-SPG', 'SPG')

def _packVehicleModel(vehicle, model):
    model.setVehicleName(getNationLessName(vehicle.name))
    model.setUserName(vehicle.shortUserName)
    model.setVehicleLvl(vehicle.level)
    model.setVehicleType(vehicle.type)
    model.setIsElite(vehicle.isElite)
    model.setNation(vehicle.nationName)


class VehicleSelectionView(ViewImpl):
    __slots__ = ('__selectedTab', '__selectVehicles', '__receivedDiscount', '__filterPopover', '__filters', '__tooltipData', '__totalRewardsCount')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = SelectableRewardViewModel()
        self.__selectedTab = 0
        self.__totalRewardsCount = 0
        self.__selectVehicles = []
        self.__filterPopover = None
        self.__filters = {}
        self.__tooltipData = {}
        self.__resetFilters(True)
        self.__receivedDiscount = sorted([ token for token in self.__itemsCache.items.tokens.getTokens().keys() if token.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX) ], key=lambda s: int(s.split(':')[-1]))
        super(VehicleSelectionView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(VehicleSelectionView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onCategorySelect, self.onTabChange),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onConfirm, self.__onConfirm),
         (self.viewModel.onSelectReward, self.__onSelectReward),
         (self.viewModel.onFilterReset, self.__resetFilters))

    def _onLoading(self, *args, **kwargs):
        super(VehicleSelectionView, self)._onLoading(*args, **kwargs)
        self.__update()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(VehicleSelectionView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyDiscountRewardTooltip():
            return NyDiscountRewardTooltip(event.getArgument('variadicID'), event.getArgument('discount'))
        return SelectedRewardsTooltip(self.__selectVehicles) if contentID == R.views.new_year.lobby.new_year.tooltips.SelectedRewardsTooltip() else super(VehicleSelectionView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        if event.contentID == R.views.new_year.lobby.new_year.popovers.VehicleFilterPopover():
            self.__filterPopover = VehicleFilterPopover(self.__filters, self.onUpdateFilter)
            return self.__filterPopover
        return super(VehicleSelectionView, self).createPopOverContent(event)

    def onTabChange(self, event):
        newTab = int(event.get('tabIndex', 0))
        self.__selectTab(newTab)

    def onUpdateFilter(self, filters=None):
        if filters:
            self.__filters = filters
        self.__updateVehicles()

    def __update(self):
        with self.viewModel.transaction() as tx:
            with tx.getCategories().transaction() as tabs:
                tabs.clear()
                for variadicID in self.__receivedDiscount:
                    variadicDiscount = VariadicDiscount(variadicID)
                    newTab = tx.getCategoriesType()()
                    newTab.setVariadicID(variadicDiscount.getID())
                    newTab.setDiscount(variadicDiscount.getDiscountValue())
                    newTab.setLevel(variadicDiscount.getTankLevel())
                    newTab.setIsSelected(False)
                    newTab.setTabIndex(len(tabs))
                    tabs.addViewModel(newTab)

                if tabs:
                    self.__selectedTab = 0
                    tabs[self.__selectedTab].setIsSelected(True)
                    self.__selectTab(self.__selectedTab)

    def __selectTab(self, tabID):
        with self.viewModel.getCategories().transaction() as tx:
            tx[self.__selectedTab].setIsSelected(False)
            tx[tabID].setIsSelected(True)
            self.__selectedTab = tabID
            self.__updateVehicles()
        self.viewModel.setTotalRewardsCount(self.__totalRewardsCount)

    def __updateVehicles(self):
        self.__totalRewardsCount = 0
        isNationsFilterEmpty = self.__isFilterEmpty(_NATIONS_KEY_NAME)
        isTypesFilterEmpty = self.__isFilterEmpty(_TYPES_KEY_NAME)
        with self.viewModel.transaction() as tx:
            variadicDiscount = VariadicDiscount(tx.getCategories()[self.__selectedTab].getVariadicID())
            vehicles = tx.getSelectableRewards()
            vehicles.clear()
            for intCD in variadicDiscount.getVehiclesByDiscount().iterkeys():
                vehicle = self.__itemsCache.items.getItemByCD(int(intCD))
                if not vehicle.isInInventory:
                    self.__totalRewardsCount += 1
                    if isNationsFilterEmpty and isTypesFilterEmpty or isTypesFilterEmpty and self.__nationFit(vehicle) or isNationsFilterEmpty and self.__typeFit(vehicle) or self.__nationFit(vehicle) and self.__typeFit(vehicle):
                        vehPrice = vehicle.getBuyPrice().price.credits
                        newVehicle = tx.getSelectableRewardsType()()
                        _packVehicleModel(vehicle, newVehicle)
                        newVehicle.setOldPrice(vehPrice)
                        newVehicle.setNewPrice(vehPrice - variadicDiscount.getDiscountValue() * vehPrice / 100)
                        newVehicle.setIsSelected(False)
                        newVehicle.setRewardIndex(len(vehicles))
                        newVehicle.setIntCD(vehicle.intCD)
                        vehicles.addViewModel(newVehicle)

            if vehicles:
                self.__setVehicleTooltipData(vehicles)
                selectRevardIndex = tx.getCategories()[self.__selectedTab].getSelectedRewardIndex()
                if selectRevardIndex != SelectableRewardCategoryModel.UNDEFIEND_REVARD_INDEX:
                    tx.getSelectableRewards()[selectRevardIndex].setIsSelected(True)
            vehicles.invalidate()

    def __onClose(self):
        self.destroyWindow()

    def __onSelectReward(self, event):
        index = int(event.get('rewardIndex', ''))
        with self.viewModel.transaction() as tx:
            vehicleModel = tx.getSelectableRewards()[index]
            currentTab = tx.getCategories()[self.__selectedTab]
            if vehicleModel.getIsSelected():
                vehicleModel.setIsSelected(False)
                self.__selectVehicles = [ t for t in self.__selectVehicles if _getVariadicID(vehicleModel.getVehicleLvl()) not in t ]
                currentTab.setSelectedVehicle('')
                currentTab.setSelectedRewardIndex(SelectableRewardCategoryModel.UNDEFIEND_REVARD_INDEX)
            else:
                curentIndexReward = currentTab.getSelectedRewardIndex()
                if curentIndexReward != SelectableRewardCategoryModel.UNDEFIEND_REVARD_INDEX:
                    prevSelectVehicle = tx.getSelectableRewards()[curentIndexReward]
                    prevSelectVehicle.setIsSelected(False)
                    self.__selectVehicles = [ t for t in self.__selectVehicles if _getVariadicID(vehicleModel.getVehicleLvl()) not in t ]
                vehicleModel.setIsSelected(True)
                self.__selectVehicles.append((vehicleModel.getIntCD(), _getVariadicID(vehicleModel.getVehicleLvl())))
                currentTab.setSelectedVehicle(vehicleModel.getVehicleName())
                currentTab.setSelectedRewardIndex(index)
            tx.setSelectedRewardsCount(len(self.__selectVehicles))

    def __isFilterEmpty(self, key):
        return not any((value for value in self.__filters[key].itervalues()))

    def __nationFit(self, vehicle):
        return self.__filters[_NATIONS_KEY_NAME][vehicle.nationName]

    def __typeFit(self, vehicle):
        return self.__filters[_TYPES_KEY_NAME][vehicle.type]

    def __resetFilters(self, init=False):
        self.__filters = {_NATIONS_KEY_NAME: OrderedDict(((nation, False) for nation in GUI_NATIONS)),
         _TYPES_KEY_NAME: OrderedDict(((t, False) for t in VEHICLE_TYPES_ORDER))}
        if self.__filterPopover and self.__filterPopover.viewStatus == ViewStatus.LOADED:
            self.__filterPopover.updateFilterFromOutside(self.__filters)
        elif not init:
            self.onUpdateFilter()

    def __onConfirm(self):
        self.__applyDiscountProcess()
        messages = []
        for vehID, variadicCategory in self.__selectVehicles:
            vehicle = self.__itemsCache.items.getItemByCD(int(vehID))
            variadicDiscount = VariadicDiscount(variadicCategory)
            messages.append(backport.text(R.strings.ny.applyVehicleDiscount.success(), discount=variadicDiscount.getDiscountValue(), vehName=str(vehicle.userName)))

        SystemMessages.pushMessage('\n'.join(messages), priority=NotificationPriorityLevel.MEDIUM, type=SM_TYPE.InformationHeader, messageData={'header': backport.text(R.strings.ny.applyVehicleDiscount.header())})

    @adisp_process('newYear/applyVehicleDiscount')
    def __applyDiscountProcess(self):
        goodiesIDs, variadicIDs = self.__prepareData()
        _ = yield ApplyVehicleDiscountProcessor(goodiesIDs, variadicIDs).request()
        self.destroyWindow()

    def __prepareData(self):
        goodies = []
        variadic = []
        for intCD, variadicID in self.__selectVehicles:
            variadicDiscount = VariadicDiscount(variadicID)
            goodiesID = variadicDiscount.getVehiclesByDiscount()[intCD]
            goodies.append(goodiesID)
            variadic.append(variadicID)

        return (goodies, variadic)

    def __setVehicleTooltipData(self, vehicles):
        tooltipIndex = 0
        self.__tooltipData = {}
        for veh in vehicles:
            veh.setTooltipId(str(tooltipIndex))
            self.__tooltipData[str(tooltipIndex)] = backport.createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_VEHICLE, specialArgs=[veh.getIntCD()])
            tooltipIndex += 1
