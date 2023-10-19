# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tank_change_view.py
import SoundGroups
from base_crew_view import BaseCrewView
from crew_sounds import SOUNDS
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.filter_panel_widget_model import FilterPanelType
from gui.impl.gen.view_models.views.lobby.crew.tank_change_vehicle_model import TankChangeVehicleModel
from gui.impl.gen.view_models.views.lobby.crew.tank_change_view_model import TankChangeViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.crew.filter import getVehicleLocationSettings, getVehicleTypeSettings, getVehicleTierSettings, getVehicleGradeSettings, GRADE_PREMIUM, SEARCH_MAX_LENGTH
from gui.impl.lobby.crew.filter.data_providers import VehiclesDataProvider
from gui.impl.lobby.crew.filter.filter_panel_widget import FilterPanelWidget
from gui.impl.lobby.crew.filter.state import FilterState
from gui.impl.lobby.crew.utils import VEHICLE_TAGS_FILTER
from gui.shared.event_dispatcher import showChangeCrewMember
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import NO_TANKMAN, MAX_ROLE_LEVEL, NO_SLOT
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewTankChangeKeys

class TankChangeView(BaseCrewView):
    __slots__ = ('__dataProvider', '__filterState', '__tankman', '__vehicle', '__selectedTmanInvID', '_filterPanelWidget')
    itemsCache = dependency.descriptor(IItemsCache)
    restore = dependency.descriptor(IRestoreController)
    platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, layoutID, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = TankChangeViewModel()
        settings.kwargs = kwargs
        self.__selectedTmanInvID = kwargs.get('tankmanInvID', NO_TANKMAN)
        self.__tankman = None
        self.__vehicle = None
        self._filterPanelWidget = None
        self.__filterState = FilterState({FilterState.GROUPS.VEHICLETYPE.value: self.getFilterTypeVehicle()})
        self.__dataProvider = VehiclesDataProvider(self.__filterState, self.tankman, self.vehicle)
        super(TankChangeView, self).__init__(settings)
        return

    @property
    def tankman(self):
        if self.__tankman is None and self.__selectedTmanInvID:
            self.__tankman = self.itemsCache.items.getTankman(self.__selectedTmanInvID)
        return self.__tankman

    @property
    def vehicle(self):
        if self.__vehicle is None:
            if self.tankman:
                self.__vehicle = self.itemsCache.items.getItemByCD(self.tankman.vehicleNativeDescr.type.compactDescr)
        return self.__vehicle

    @property
    def viewModel(self):
        return super(TankChangeView, self).getViewModel()

    def getFilterTypeVehicle(self):
        return self.tankman.getVehicle().type if self.tankman and self.tankman.isInTank else self.vehicle.type

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(TankChangeView, self).createToolTip(event)

    @staticmethod
    def getTooltipData(event):
        return backport.createTooltipData(specialAlias=event.getArgument('tooltipId'), isSpecial=True, specialArgs=(event.getArgument('vehicleCD'),))

    def _setWidgets(self, **kwargs):
        super(TankChangeView, self)._setWidgets(**kwargs)
        self._filterPanelWidget = FilterPanelWidget(getVehicleLocationSettings(), (getVehicleTypeSettings(R.strings.crew.filter.group.vehicleType.tankChange.title()), getVehicleTierSettings(R.strings.crew.filter.group.vehicleTier.shortTitle()), getVehicleGradeSettings((GRADE_PREMIUM,))), R.strings.crew.filter.popup.tankChange.title(), self.__filterState, panelType=FilterPanelType.TANKCHANGE, isSearchEnabled=True, popoverTooltipHeader=R.strings.crew.tankChange.tooltip.popover.header(), popoverTooltipBody=R.strings.crew.tankChange.tooltip.popover.body(), searchTooltipBody=backport.text(R.strings.crew.tankChange.tooltip.searchInput.body(), maxLength=SEARCH_MAX_LENGTH))
        self.setChildView(FilterPanelWidget.LAYOUT_ID(), self._filterPanelWidget)

    def _fillViewModel(self, vm):
        super(TankChangeView, self)._fillViewModel(vm)
        vm.setNation(self.vehicle.nationName)
        self.__dataProvider.update()

    def _onLoading(self, *args, **kwargs):
        super(TankChangeView, self)._onLoading(*args, **kwargs)
        self.__dataProvider.update()

    def _finalize(self):
        super(TankChangeView, self)._finalize()
        self._filterPanelWidget = None
        self.__filterState = None
        self.__dataProvider.clear()
        self.__dataProvider = None
        if not self.vehicle or not self.vehicle.hasCrew:
            self._destroySubViews()
        self._clear()
        return

    def _clear(self):
        self.__selectedTmanInvID = None
        self.__tankman = None
        self.__vehicle = None
        return

    def _getEvents(self):
        eventsTuple = super(TankChangeView, self)._getEvents()
        return eventsTuple + ((self.viewModel.onResetFilters, self._onResetFilters),
         (self.viewModel.onVehicleSelected, self._onVehicleSelected),
         (self.__dataProvider.onDataChanged, self.__updateModelsData),
         (self.__filterState.onStateChanged, self._onFilterStateUpdated),
         (self.platoonCtrl.onMembersUpdate, self._onMembersUpdate))

    def _getCallbacks(self):
        return (('inventory', self._onInventoryUpdate), ('inventory.8.compDescr', self._onVehicleUpdated))

    def _onClose(self, params=None):
        self._logClose(params)
        self._onBack(False)

    def _onMembersUpdate(self):
        self.destroyWindow()

    def _onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff or GUI_ITEM_TYPE.VEHICLE in invDiff:
            if self.tankman:
                self.__updateModelsData()

    def _onTankmanSlotAutoSelect(self, tankmanID, slotIdx):
        if self.__selectedTmanInvID == tankmanID:
            return
        self._clear()
        if tankmanID != NO_TANKMAN:
            self.__tankman = self.itemsCache.items.getTankman(tankmanID)
        self.__selectedTmanInvID = tankmanID
        self.__dataProvider.reinit(self.tankman, self.vehicle)
        self.__dataProvider.update()

    def _onTankmanSlotClick(self, tankmanInvID, slotIdx):
        self._onTankmanSlotAutoSelect(tankmanInvID, slotIdx)

    def _findWidgetSlotNextIdx(self, tankmanID, slotIDX):
        if tankmanID != NO_TANKMAN:
            newSlotIDX, _ = self._currentSlotAndTankman(tankmanID)
            slotIDX = newSlotIDX if newSlotIDX != NO_TANKMAN else slotIDX
            return self._getAutoSelectWidget(tankmanID, slotIDX)
        return (NO_TANKMAN, NO_SLOT)

    def _onEmptySlotClick(self, tankmanID, slotIdx):
        showChangeCrewMember(slotIdx, self.vehicle.invID, self.layoutID)

    def _onFilterStateUpdated(self):
        self.__dataProvider.update()

    def _onResetFilters(self):
        self._filterPanelWidget.resetState()
        self._filterPanelWidget.applyStateToModel()

    @args2params(int)
    def _onVehicleSelected(self, vehicleID):
        self._uiLogger.logClick(CrewTankChangeKeys.CARD)
        vehicle = self.itemsCache.items.getItemByCD(vehicleID)
        if not vehicle:
            return
        dialogs.showRetrainDialog([self.tankman.invID], vehicleID)
        SoundGroups.g_instance.playSound2D(SOUNDS.CREW_TANK_CLICK)

    def _onVehicleUpdated(self, _):
        lastVehicleCD = self.vehicle.compactDescr
        self.__tankman = None
        self.__vehicle = None
        if self.vehicle and lastVehicleCD != self.vehicle.compactDescr:
            self.__dataProvider.updateRoot(self.vehicle)
            self.__dataProvider.update()
        return

    def __updateModelsData(self):
        self.__tankman = self.itemsCache.items.getTankman(self.__selectedTmanInvID)
        if self.__tankman:
            with self.viewModel.transaction() as tx:
                self.__fillVehicleList(tx)

    def __isValidForTraining(self, vehicle):
        return not (self.tankman.vehicleNativeDescr.type.compactDescr == vehicle.compactDescr and self.tankman.roleLevel >= MAX_ROLE_LEVEL)

    def __fillVehicleList(self, tx):
        filteredVehicles = self.__dataProvider.items()
        self._filterPanelWidget.updateAmountInfo(self.__dataProvider.itemsCount, self.__dataProvider.initialItemsCount)
        vehicleList = tx.getVehicleList()
        vehicleList.clear()
        for _, vehicle in enumerate(filteredVehicles):
            vm = TankChangeVehicleModel()
            fillVehicleModel(vm, vehicle, VEHICLE_TAGS_FILTER)
            vm.setIsPremium(vehicle.isPremium)
            vm.setIsElite(vehicle.isElite)
            vm.setIsSelected(self.vehicle.compactDescr == vehicle.compactDescr)
            vm.setIsInInventory(vehicle.isInInventory)
            vm.setIsTrainingAvailable(self.__isValidForTraining(vehicle))
            vehicleList.addViewModel(vm)

        vehicleList.invalidate()
