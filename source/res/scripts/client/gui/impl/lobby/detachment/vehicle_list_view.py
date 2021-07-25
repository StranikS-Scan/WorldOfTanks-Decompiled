# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/vehicle_list_view.py
import logging
from copy import deepcopy
from CurrentVehicle import g_currentVehicle
from async import async, await
from constants import VEHICLE_NO_INV_ID
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.impl.auxiliary.instructors_helper import fillVehicleModel
from gui.impl.auxiliary.detachment_helper import fillDetachmentShortInfoModel, hasCrewTrainedForVehicle
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.dialogs.dialogs import showTrainVehicleConfirmView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.filter_status_model import FilterStatusModel
from gui.impl.gen.view_models.views.lobby.detachment.vehicle_card_model import VehicleCardModel
from gui.impl.gen.view_models.views.lobby.detachment.vehicle_list_view_model import VehicleListViewModel
from gui.impl.lobby.detachment.list_filter_mixin import FiltersMixin, FilterContext
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.popovers import getVehicleTypeSettings, getVehicleLevelSettings, PopoverFilterGroups
from gui.impl.lobby.detachment.popovers.filters.vehicle_filters import defaultVehiclePopoverFilter, defaultVehicleToggleFilter, popoverCriteria, toggleCriteria, TOGGLE_FILTERS_ORDER
from gui.impl.lobby.detachment.popovers.toggle_filter_popover_view import ToggleFilterPopoverViewStatus
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.commander_perk_tooltip import CommanderPerkTooltip
from gui.impl.lobby.detachment.ttc_mixin import TTCMixin
from gui.shared.event_dispatcher import isViewLoaded
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.processors.detachment import DetachmentSpecializeVehicleSlot, DetachmentSwapVehicleSlots
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import ITEM_TYPES
from items.vehicles import makeVehicleTypeCompDescrByName
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from sound_constants import BARRACKS_SOUND_SPACE
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import DetachmentToggleLogger, g_detachmentFlowLogger
_logger = logging.getLogger(__name__)

class VehicleListView(TTCMixin, FiltersMixin, NavigationViewImpl):
    __slots__ = ('_suitableVehCriteria', '_vehicleCollection', '__detachment', '__detachmentInvID', '__vehicleSlotIndex', '__vehicleSlots', '__vehicleSlotCD', '_filtersCtx', '_defaultPopoverFilterItems')
    _CLOSE_IN_PREBATTLE = True
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    __itemsCache = dependency.descriptor(IItemsCache)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    _defaultPopoverSetter = staticmethod(defaultVehiclePopoverFilter)
    _defaultToggleSetter = staticmethod(defaultVehicleToggleFilter)
    _popoverFilters = defaultVehiclePopoverFilter()
    _toggleFilters = defaultVehicleToggleFilter()
    uiLogger = DetachmentToggleLogger(GROUP.SPECIALIZATION_VEHICLE_LIST_CHOICE)

    def __init__(self, ctx=None):
        settings = ViewSettings(R.views.lobby.detachment.VehicleListView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = VehicleListViewModel()
        super(VehicleListView, self).__init__(settings, ctx=ctx)
        self.__detachmentInvID = self._navigationViewSettings.getViewContextSettings().get('detInvID')
        self.__vehicleSlotIndex = self._navigationViewSettings.getViewContextSettings().get('vehicleSlotIndex')
        self.__detachment = self.__detachmentCache.getDetachment(self.__detachmentInvID)
        self._suitableVehCriteria = self._buildSuitableVehCriteria()
        self._vehicleCollection = self.__itemsCache.items.getVehicles(self._suitableVehCriteria)
        self._filtersCtx = {'currentCount': 0,
         'totalCount': 0}
        super(VehicleListView, self)._resetData()
        VehicleListView._defaultPopoverFilterItems = deepcopy(self._popoverFilters.items())

    def createPopOverContent(self, event):
        ToggleFilterPopoverViewStatus.uiLogger.setGroup(self.uiLogger.group)
        return ToggleFilterPopoverViewStatus(R.strings.detachment.toggleFilterPopover.header(), R.strings.detachment.filterStatus.vehicle(), FilterStatusModel.DIVIDER, (getVehicleTypeSettings(R.strings.tooltips.filterToggle.vehicleType.vehicle.body(), R.strings.detachment.toggleFilterPopover.group.vehicleType.label()), getVehicleLevelSettings()), self._changePopoverFilterCallback, self._activatePopoverViewCallback, VehicleListView._popoverFilters, self._filtersCtx, customResetFunc=self._resetPopoverFilters)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instructorID = event.getArgument('instructorInvID')
            tooltip = getInstructorTooltip(instructorInvID=instructorID, detachment=self.__detachment)
            if hasattr(tooltip, 'uiLogger'):
                tooltip.uiLogger.setGroup(self.uiLogger.group)
            return tooltip
        if event.contentID == R.views.lobby.detachment.tooltips.CommanderPerkTooltip():
            perkType = event.getArgument('perkType')
            return CommanderPerkTooltip(perkType=perkType)
        if contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
            DetachmentInfoTooltip.uiLogger.setGroup(self.uiLogger.group)
            return DetachmentInfoTooltip(detachmentInvID=self.__detachmentInvID)
        if contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip():
            LevelBadgeTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return LevelBadgeTooltipView(self.__detachmentInvID)

    def createToolTip(self, event):
        tooltipId = event.getArgument('tooltipId', None)
        vehId = event.getArgument('vehId', None)
        args = None
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            if tooltipId == TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE:
                args = [vehId]
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args), self.getParentWindow())
            window.load()
            return window
        else:
            return super(VehicleListView, self).createToolTip(event)

    @property
    def viewModel(self):
        return super(VehicleListView, self).getViewModel()

    def _initModel(self, vm):
        super(VehicleListView, self)._initModel(vm)
        self._initFilters(vm, TOGGLE_FILTERS_ORDER, FilterContext.VEHICLE)
        self.__fillViewModel(vm)

    def _initialize(self, *args, **kwargs):
        super(VehicleListView, self)._initialize()
        self.uiLogger.startAction(ACTION.OPEN)
        self._updateTTCCurrentDetachment(self.__detachmentInvID)
        self._updateTTCVehicle()

    def _finalize(self):
        g_detachmentTankSetupVehicle.restoreCurrentVehicle()
        self.uiLogger.stopAction(ACTION.OPEN)
        super(VehicleListView, self)._finalize()

    def _addListeners(self):
        super(VehicleListView, self)._addListeners()
        self.viewModel.onItemClick += self.__onItemClick
        self.viewModel.onItemHover += self.__onItemHover
        self._subscribeFilterHandlers(self.viewModel)
        g_clientUpdateManager.addCallbacks({'inventory.{}'.format(ITEM_TYPES.detachment): self.__onClientUpdate,
         'inventory.{}'.format(ITEM_TYPES.vehicle): self.__onClientUpdate,
         'cache.vehsLock': self.__onClientUpdate})

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.viewModel.onItemClick -= self.__onItemClick
        self.viewModel.onItemHover -= self.__onItemHover
        self._unsubscribeFilterHandlers(self.viewModel)
        super(VehicleListView, self)._removeListeners()

    def _fillList(self, model):
        vehicles = self.__getVehicles()
        filteredCount = len(vehicles)
        self._setTTCVisibility(filteredCount > 0)
        self._filtersCtx['currentCount'] = filteredCount
        model.filtersModel.setCurrent(filteredCount)
        vehicleCDs = self.__detachment.getVehicleCDs()
        slotVehicleCD = vehicleCDs[self.__vehicleSlotIndex]
        vehiclesListModel = model.vehicles
        vehiclesListModel.clearItems()
        for intCD, vehicle in vehicles:
            vehicleModel = VehicleCardModel()
            fillVehicleModel(vehicleModel, vehicle)
            if hasCrewTrainedForVehicle(intCD):
                vehicleModel.setStatus(VehicleCardModel.HAS_CREW)
            elif vehicle.isInInventory:
                vehicleModel.setStatus(VehicleCardModel.IN_HANGAR)
            else:
                vehicleModel.setStatus(VehicleCardModel.DEFAULT)
            vehicleModel.setCardState(VehicleCardModel.DEFAULT)
            if vehicle.intCD == slotVehicleCD:
                model.setSelectedVehicleName(vehicle.userName)
                vehicleModel.setCardState(VehicleCardModel.SELECTED)
            elif vehicle.intCD in vehicleCDs:
                vehicleModel.setCardState(VehicleCardModel.LEARNED)
            if vehicle.isInBattle:
                vehicleModel.setCardState(VehicleCardModel.IN_BATTLE)
            if vehicle.isInUnit:
                vehicleModel.setCardState(VehicleCardModel.IN_PLATOON)
            model.vehicles.addViewModel(vehicleModel)

        vehiclesListModel.invalidate()

    def _resetData(self):
        super(VehicleListView, self)._resetData()
        self._resetPopover()

    def _resetPopoverFilters(self):
        super(VehicleListView, self)._resetPopoverFilters()
        self._resetPopover()

    def _resetPopover(self):
        if not self.__getVehicles():
            VehicleListView._popoverFilters.update(self._defaultPopoverSetter())
        VehicleListView._defaultPopoverFilterItems = deepcopy(self._popoverFilters.items())

    def _buildSuitableVehCriteria(self):
        vehicleCDs = self.__detachment.getVehicleCDs()
        slotVehicleCD = vehicleCDs[self.__vehicleSlotIndex]
        criteria = ~REQ_CRITERIA.VEHICLE.PREMIUM
        criteria |= ~REQ_CRITERIA.SECRET
        criteria |= ~REQ_CRITERIA.VEHICLE.EVENT
        criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        criteria |= REQ_CRITERIA.NATIONS((self.__detachment.nationID,))
        if slotVehicleCD is None:
            criteria |= ~REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(vehicleCDs)
        return criteria

    def _updateTTCVehicle(self, vehicleCD=None):
        if vehicleCD is None:
            vehicleCD = self.__detachment.getVehicleCDs()[self.__vehicleSlotIndex]
        if vehicleCD is None:
            observerCD = makeVehicleTypeCompDescrByName('ussr:Observer')
            vehicleGuiIt = self.__itemsCache.items.getItemByCD(observerCD)
        else:
            vehicleGuiIt = self.__itemsCache.items.getItemByCD(vehicleCD)
        super(VehicleListView, self)._updateTTCVehicle(vehicleGuiIt)
        super(VehicleListView, self)._updateTTCBonusDetachment(self.__detachmentInvID)
        return

    def _addDefaultPopoverFilter(self):
        VehicleListView._popoverFilters[PopoverFilterGroups.VEHICLE_TYPE].add(self.__detachment.classType)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.DETACHMENT_PERSONAL_CASE)
    def _onEscape(self):
        self._onBack()

    def __fillViewModel(self, model):
        fillDetachmentShortInfoModel(model.detachmentInfo, self.__detachment)
        totalCount = len(self._vehicleCollection)
        model.filtersModel.setTotal(totalCount)
        self._filtersCtx['totalCount'] = totalCount
        self._fillList(model)

    def __getVehicles(self):
        criteria = popoverCriteria(VehicleListView._popoverFilters)
        criteria |= toggleCriteria([ fName for fName, active in self._toggleFilters.iteritems() if active ])
        vehicles = self._vehicleCollection.filter(criteria)
        self.__vehicleSlots = self.__detachment.getVehicleCDs()
        self.__vehicleSlotCD = self.__vehicleSlots[self.__vehicleSlotIndex]
        return sorted(vehicles.iteritems(), key=self.__vehicleSortingValue)

    def __onClientUpdate(self, diff):
        self.__detachment = self.__detachmentCache.getDetachment(self.__detachmentInvID)
        self._vehicleCollection = self.__itemsCache.items.getVehicles(self._suitableVehCriteria)
        with self.viewModel.transaction() as model:
            self.__fillViewModel(model)

    def __onItemClick(self, args=None):
        if args is None:
            _logger.error('args=None. Please fix JS')
            return
        elif isViewLoaded(R.views.lobby.detachment.dialogs.TrainVehicleConfirmView()):
            return
        else:
            vehicleCD = int(args.get('vehicleId'))
            self.__selectedVehicleCD = vehicleCD
            vehicleCDs = self.__detachment.getVehicleCDs()
            try:
                slot2Index = vehicleCDs.index(self.__selectedVehicleCD)
            except ValueError:
                self.__trainForVehicle()
            else:
                self.__swapVehicleSlots(slot2Index)

            return

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.TRAIN_VEHICLE_CONFIRM_DIALOG)
    @async
    def __trainForVehicle(self):
        sdr = yield await(showTrainVehicleConfirmView(self.getParentWindow(), detachmentInvID=self.__detachmentInvID, slotIndex=self.__vehicleSlotIndex, selectedVehicleCD=self.__selectedVehicleCD))
        result, args = sdr.result
        if result and args:
            self.__specializeVehicleSlot(args.get('paymentOptionIdx'), args.get('isReset'))

    @decorators.process('updating')
    def __specializeVehicleSlot(self, payIndex, isReset):
        selectedVehicleCD = self.__selectedVehicleCD
        processor = DetachmentSpecializeVehicleSlot(self.__detachmentInvID, self.__vehicleSlotIndex, selectedVehicleCD, payIndex, int(isReset))
        result = yield processor.request()
        SystemMessages.pushMessages(result)
        if result.success:
            vehicle = self.__itemsCache.items.getItemByCD(selectedVehicleCD)
            if vehicle and vehicle.invID != VEHICLE_NO_INV_ID:
                g_currentVehicle.selectVehicle(vehicle.invID)
            self._onEscape()

    @decorators.process('updating')
    def __swapVehicleSlots(self, slot2Index):
        processor = DetachmentSwapVehicleSlots(self.__detachmentInvID, slot1Index=self.__vehicleSlotIndex, slot2Index=slot2Index)
        result = yield processor.request()
        SystemMessages.pushMessages(result)

    def __onItemHover(self, args=None):
        if args is not None:
            ttcVehicleCD = int(args.get('vehicleId'))
            self._updateTTCVehicle(ttcVehicleCD)
        else:
            self._updateTTCVehicle()
        return

    def __vehicleSortingValue(self, item):
        _, vehicle = item
        isOwnedOrder = vehicle.inventoryCount < 1
        typeOrder = Vehicle.VEHICLE_TYPES_ORDER_INDICES[vehicle.type]
        compositeKey = (isOwnedOrder,
         not vehicle.hasDetachment,
         not vehicle.isLocked,
         vehicle.level,
         typeOrder,
         vehicle.userName)
        if self.__vehicleSlotCD is not None:
            currentVehOrder = self.__vehicleSlotCD != vehicle.intCD
            learnedVehOrder = vehicle.intCD not in self.__vehicleSlots
            compositeKey = (currentVehOrder, learnedVehOrder) + compositeKey
        return compositeKey
