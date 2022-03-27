# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/rts_roster_view.py
import typing
import logging
from functools import partial
from typing import TYPE_CHECKING
import BigWorld
import AccountCommands
from account_helpers.AccountSettings import RTS_ROSTER_FILTER_CLIENT
from account_helpers.client_ai_rosters import getSuitableVehicleCriteriaForRoster
from async import async, await, AsyncScope
from BWUtil import AsyncReturn
from frameworks.wulf import ViewFlags, ViewModel, ViewSettings, Array, WindowFlags
from gui import GUI_NATIONS_ORDER_INDEX, SystemMessages
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_view_model import RosterVehicleViewModel, MannerEnum
from gui.impl.gen.view_models.views.lobby.rts.carousel_supply_slot_model import CarouselSupplySlotModel
from gui.impl.gen.view_models.views.lobby.rts.carousel_vehicle_slot_model import CarouselVehicleSlotModel
from gui.impl.gen.view_models.views.lobby.rts.carousel_view_model import CarouselViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_supply_view_model import RosterSupplyViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_view_model import RosterViewModel
from gui.impl.lobby.rts.model_helpers import buildVehicleSlotModel, buildSupplySlotModel, fillRosterSupplyModel, packVehicleBaseModel, packRosterVehicleModel, swapRosterVehicleViewModel, swapSupplyModel, getGameMode, SUPPLY_ENUM_TO_ID
from gui.impl.lobby.rts.rts_manners_settings import RtsMannersSettings
from gui.impl.pub import ViewImpl, WindowImpl
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import ICarouselEnvironment
from gui.impl.gui_decorators import args2params
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from gui.shared.events import CloseWindowEvent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_CLASS_NAME, VEHICLE_TYPES_ORDER_INDICES, VEHICLE_TYPES_ORDER, getIconShopResource
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.rts_battles.rts_constants import RTS_CAROUSEL_FILTER_KEY
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import SessionCarouselFilter, BasicCriteriesGroup
from gui.impl.lobby.rts.vehicle_specs.rts_roster_vehicle_specs import RosterVehicleSpecs
from gui.impl.lobby.rts.vehicle_specs.rts_vehicle_builder import RtsVehicleBuilder
from gui.impl.lobby.rts.vehicle_specs.rts_vehicle_parameters import RtsVehicleParameters
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen.view_models.views.lobby.rts.roster_view.supply_details_tooltip_model import SupplyDetailsTooltipModel
from RTSShared import RTSSupply, RTSManner
if TYPE_CHECKING:
    from typing import List, Tuple, Dict
_logger = logging.getLogger(__name__)

def _saveCallback(_, resultID, errorStr, ___=None):
    _logger.debug('[ROSTER_VIEW] _saveCallBack, result id %d', resultID)
    if resultID != AccountCommands.RES_SUCCESS:
        _logger.warning('Roster save failed: %s', errorStr)
        saveErrorMsg = backport.text(R.strings.rts_battles.notifications.saveError())
        SystemMessages.pushMessage(saveErrorMsg, type=SystemMessages.SM_TYPE.Error)


class RTSRosterFilter(SessionCarouselFilter):

    def __init__(self):
        super(RTSRosterFilter, self).__init__()
        self._clientSections = (RTS_ROSTER_FILTER_CLIENT,)


class RTSRosterCriteriesGroup(BasicCriteriesGroup):

    def update(self, filters):
        super(RTSRosterCriteriesGroup, self).update(filters)
        if filters[RTS_CAROUSEL_FILTER_KEY]:
            self._criteria |= ~REQ_CRITERIA.VEHICLE.HAS_CUSTOM_STATE(Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE)


class RosterView(ViewImpl, ICarouselEnvironment):
    __slots__ = ('_filter', '_popoverCloseCallback', '_rosterConfig', '__battleType', '_slotCache', '_filteredIntCDs', '__blur', '__isClosed', '__closeConfirmationHelper', '_selectedSupplySlot', '_selectedVehicleSlot', '_isModified', '_vehicleSpecs', '_mannersSettings')
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _rtsController = dependency.descriptor(IRTSBattlesController)
    _EMPTY_SLOT = 0
    _UNSELECTED = -1

    def __init__(self, layoutID, battleType, selectedSupplySlot, selectedVehicleSlot):
        settings = ViewSettings(layoutID=layoutID, flags=ViewFlags.LOBBY_SUB_VIEW, model=RosterViewModel())
        super(RosterView, self).__init__(settings)
        self._filter = RTSRosterFilter()
        self._filter.load()
        self._filter.reset()
        self._popoverCloseCallback = None
        rostersConfig = self._lobbyContext.getServerSettings().getAIRostersConfig()
        self._rosterConfig = rostersConfig.get(battleType, {})
        self.__battleType = battleType
        self._slotCache = {}
        self._filteredIntCDs = []
        self.__blur = CachedBlur()
        self.__isClosed = False
        self.__closeConfirmationHelper = CloseConfirmatorsHelper()
        self._vehicleSpecs = RosterVehicleSpecs(self.viewModel.vehicleSpecs)
        self._scope = AsyncScope()
        roster = self._itemsCache.items.aiRosters.getRosters().get(self.__battleType, {})
        self._mannersSettings = RtsMannersSettings(roster)
        if selectedSupplySlot is self._UNSELECTED and selectedVehicleSlot is self._UNSELECTED:
            vehicles = roster.get('vehicles', [])
            supplies = roster.get('supplies', [])
            if self._EMPTY_SLOT in vehicles:
                selectedVehicleSlot = vehicles.index(self._EMPTY_SLOT)
            elif self._EMPTY_SLOT in supplies:
                selectedSupplySlot = supplies.index(self._EMPTY_SLOT)
            else:
                selectedVehicleSlot = 0
        self._selectedSupplySlot = selectedSupplySlot
        self._selectedVehicleSlot = selectedVehicleSlot
        self._isModified = False
        return

    @property
    def viewModel(self):
        return super(RosterView, self).getViewModel()

    @property
    def filter(self):
        return self._filter

    def createPopOverContent(self, event):
        _logger.info('CreatePopoverContent: %s', str(event))
        return BackportPopOverContent(createPopOverData(VIEW_ALIAS.RTS_ROSTER_FILTER_POPOVER, self))

    def createToolTip(self, event):
        _logger.debug('[ROSTER_VIEW] createToolTip: %s', str(event))
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            window = self._createBackportTooltip(event)
            if window:
                window.load()
            return window
        return super(RosterView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.rts.MannersTooltip():
            return ViewImpl(ViewSettings(contentID, model=ViewModel()))
        if contentID == R.views.lobby.rts.SupplyDetailsTooltip():
            supplyType = event.getArgument('type')
            intCD = int(event.getArgument('intCD'))
            model = SupplyDetailsTooltipModel()
            model.setType(supplyType)
            supply = RtsVehicleBuilder().createVehicle(intCD)
            RtsVehicleParameters(model.parameters).setVehicle(supply, forceUpdate=True)
            return ViewImpl(ViewSettings(contentID, model=model))
        return super(RosterView, self).createToolTipContent(event=event, contentID=contentID)

    def applyFilter(self):
        with self.viewModel.transaction() as model:
            self._invalidateGrid(model, self._getSlotCtx())

    def blinkCounter(self):
        pass

    def formatCountVehicles(self):
        return len(self.viewModel.getVehicles())

    def updateHotFilters(self):
        pass

    def getSelectedSlotSupportedTypes(self):
        return self._getSlotSupportedTypes(self._selectedVehicleSlot)

    def setPopoverCallback(self, callback=None):
        self._popoverCloseCallback = callback

    def _initialize(self):
        _logger.debug('[ROSTER_VIEW] _initialize')
        super(RosterView, self)._initialize(self)
        self.viewModel.onAcceptClicked += self._onSave
        self.viewModel.onClose += self._onClose
        self.viewModel.onCancelClicked += self._onCancelClicked
        self.viewModel.onItemClicked += self._onItemClicked
        self.viewModel.onClearVehicleSlotClicked += self._onClearVehicleSlotClicked
        self.viewModel.onClearSupplySlotClicked += self._onClearSupplySlotClicked
        self.viewModel.onFilterClearClicked += self._onFilterClearClicked
        self.viewModel.carousel.onVehicleSlotClicked += self._onVehicleSlotClicked
        self.viewModel.carousel.onSupplySlotClicked += self._onSupplySlotClicked
        self.viewModel.onFilterTextChanged += self._onFilterTextChanged
        self.viewModel.onClosingAnimationEnded += self._destroy
        self.viewModel.onMannerClicked += self._onMannerClicked
        self.__closeConfirmationHelper.start(self.__closeConfirmation)
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged

    def _finalize(self):
        _logger.debug('[ROSTER_VIEW] _finalize')
        self.viewModel.onAcceptClicked -= self._onSave
        self.viewModel.onClose -= self._onClose
        self.viewModel.onCancelClicked -= self._onCancelClicked
        self.viewModel.onItemClicked -= self._onItemClicked
        self.viewModel.onClearVehicleSlotClicked -= self._onClearVehicleSlotClicked
        self.viewModel.onClearSupplySlotClicked -= self._onClearSupplySlotClicked
        self.viewModel.onFilterClearClicked -= self._onFilterClearClicked
        self.viewModel.carousel.onVehicleSlotClicked -= self._onVehicleSlotClicked
        self.viewModel.carousel.onSupplySlotClicked -= self._onSupplySlotClicked
        self.viewModel.onFilterTextChanged -= self._onFilterTextChanged
        self.viewModel.onClosingAnimationEnded -= self._destroy
        self.viewModel.onMannerClicked -= self._onMannerClicked
        self.__closeConfirmationHelper.stop()
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        self._scope.destroy()
        if self.__blur is not None:
            self.__blur.fini()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)
        soundManger = self._rtsController.getSoundManager()
        soundManger.onCloseRosterSetup()
        super(RosterView, self)._finalize()
        return

    @classmethod
    def _vehicleCmpKey(cls, vehicle):
        return (GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         vehicle.userName)

    def _onLoading(self, *args, **kwargs):
        _logger.debug('[ROSTER_VIEW] _onLoading')
        super(RosterView, self)._onLoading(*args, **kwargs)
        self._updateGameModeValue()
        roster = self._itemsCache.items.aiRosters.getRosters().get(self.__battleType, {})
        with self.viewModel.transaction() as model:
            carousel = model.carousel
            self._buildCarouselModel(roster, carousel)
            self._fillSlotsVehicleClass(model)
            self._invalidateAll(model)
        self._updateVehicleSpecsSelection()

    def _onLoaded(self, *args, **kwargs):
        _logger.debug('[ROSTER_VIEW] _onLoaded')
        super(RosterView, self)._onLoading(*args, **kwargs)
        self.__blur.enable()
        soundManager = self._rtsController.getSoundManager()
        soundManager.onOpenRosterSetup()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)

    def _buildCarouselModel(self, roster, model):
        supplies = roster.get('supplies', [])
        vehicles = roster.get('vehicles', [])
        self._fillSupplySlots(supplies, model.getSupplySlots())
        self._fillVehicleSlots(vehicles, model.getVehicleSlots())
        model.setSelectedSupplySlot(self._selectedSupplySlot)
        model.setSelectedVehicleSlot(self._selectedVehicleSlot)

    def _updateSupplyLimits(self, supplyArray):
        supplyTypeToNumberInBattle = self._getSupplyTypeToNumberInBattle()
        for supplyModel in supplyArray:
            supplyid = SUPPLY_ENUM_TO_ID[supplyModel.getType()]
            supplyType = RTSSupply.SUPPLY_ID_TO_TAG[supplyid]
            if supplyType in supplyTypeToNumberInBattle:
                supplyModel.setDefenseCount(supplyTypeToNumberInBattle[supplyType])

    def _fillSupplySlots(self, roster, slotArray):
        numOfSlots = self._rosterConfig.get('supplies', {}).get('slots', 0)
        slotArray.clear()
        slotArray.reserve(numOfSlots)
        rosterSize = len(roster)
        for slotIndex in range(numOfSlots):
            slotModel = CarouselSupplySlotModel()
            if rosterSize > slotIndex:
                buildSupplySlotModel(roster[slotIndex], slotModel, self._getSupplyTypeToNumberInBattle())
            slotArray.addViewModel(slotModel)

        slotArray.invalidate()

    def _fillVehicleSlots(self, roster, slotArray):
        numOfSlots = self._rosterConfig.get('vehicles', {}).get('slots', 0)
        slotArray.clear()
        slotArray.reserve(numOfSlots)
        rosterSize = len(roster)
        for slotIndex in range(numOfSlots):
            slotModel = CarouselVehicleSlotModel()
            if rosterSize > slotIndex:
                buildVehicleSlotModel(roster[slotIndex], slotModel, self._getManner)
            slotArray.addViewModel(slotModel)

        slotArray.invalidate()

    def _fillSlotsVehicleClass(self, model):
        slotClassArray = model.getSlotVehicleClasses()
        config = self._rosterConfig.get('vehicles', {}).get('bots', [])
        for vehicleConfig in config:
            slotClassArray.addArray(self._buildSupportedTypesArray(vehicleConfig))

    def _getSupportedVehicleTypes(self, vehicleConfig):
        allowedTypes = [ tag for tag in vehicleConfig.get('allowedTags', []) if tag in VEHICLE_CLASS_NAME.ALL() ]
        return allowedTypes or VEHICLE_TYPES_ORDER

    def _buildSupportedTypesArray(self, vehicleConfig):
        result = Array()
        allowedTypes = self._getSupportedVehicleTypes(vehicleConfig)
        allowedTypes = sorted(allowedTypes, key=lambda _type: VEHICLE_TYPES_ORDER_INDICES[_type])
        for allowedType in allowedTypes:
            result.addString(allowedType)

        result.invalidate()
        return result

    def _fillGrid(self, items, modelArray, ctx):
        _logger.debug('[ROSTER_VIEW] _fillGrid')
        if set([ veh.getIntCD() for veh in modelArray ]) == set(items):
            return
        slotCache = self._slotCache
        modelPacker = ctx['modelPacker']
        modelClass = ctx['modelClass']
        allowedTags = ctx['allowedTags']
        criteria = REQ_CRITERIA.EMPTY
        if allowedTags:
            criteria |= REQ_CRITERIA.VEHICLE.HAS_ANY_OF_TAGS(allowedTags)
        modelArray.clear()
        modelArray.reserve(len(items))
        for intCD in items:
            model = modelClass()
            item = slotCache[intCD]
            modelPacker(item, model)
            if not criteria(item):
                model.setIsUnsuitable(True)
            modelArray.addViewModel(model)

        modelArray.invalidate()

    def _invalidateGrid(self, model, ctx):
        if self._isVehicleSelected():
            vehicles = self._getCurrentvehicles()
            self._fillGrid(vehicles, model.getVehicles(), ctx)
        else:
            supplies = model.getSupplies()
            self._fillGrid(self._filteredIntCDs, supplies, ctx)
            self._updateSupplyLimits(supplies)

    def _invalidateGridManners(self, vehicles):
        for veh in vehicles:
            veh.setManner(MannerEnum(self._getManner(veh.getIntCD())))

    def _invalidateAll(self, model):
        _logger.debug('[ROSTER_VIEW] _invalidateAll')
        ctx = self._getSlotCtx()
        self._invalidateFilterCache(ctx)
        model.setTotalItems(len(self._filteredIntCDs))
        self._filter.reset()
        allowedTags = ctx['allowedTags']
        for tag in allowedTags:
            self._filter.switch(tag)

        self._invalidateGrid(model, ctx if ctx else self._getSlotCtx())

    def _invalidateFilterCache(self, ctx):
        _logger.debug('[ROSTER_VIEW] _invalidateFilterCache')
        self._filteredIntCDs[:] = []
        self._slotCache.clear()
        suitable = self._itemsCache.items.getVehicles(ctx['criteria']).values()
        for vehicle in sorted(suitable, key=self._vehicleCmpKey):
            intCD = vehicle.intCD
            self._slotCache.setdefault(intCD, vehicle)
            self._filteredIntCDs.append(intCD)

        _logger.info('Filtered vehicles: %d', len(self._filteredIntCDs))

    def _createBackportTooltip(self, event):
        if not event.hasArgument('specialAlias'):
            _logger.warning('[ROSTER_VIEW] Requested backport tooltip but specialAlias is missing!')
            return
        else:
            specialAlias = event.getArgument('specialAlias')
            specialArgs = None
            if specialAlias == TOOLTIPS_CONSTANTS.RTS_VEHICLE_PARAMETERS:
                parameterName = event.getArgument('name')
                specialArgs = [parameterName]
            elif specialAlias == TOOLTIPS_CONSTANTS.RTS_VEHICLE_RESTRICTIONS:
                slotIdx = event.getArgument('slotIndex')
                specialArgs = [self._getSlotSupportedTypes(slotIdx)]
            elif specialAlias == TOOLTIPS_CONSTANTS.PREVIEW_CREW_SKILL:
                skillId = event.getArgument('skillId')
                specialArgs = [skillId]
            elif specialAlias == TOOLTIPS_CONSTANTS.RTS_ROSTER_TANKMAN:
                role = event.getArgument('role')
                specialArgs = [role]
            elif specialAlias in [TOOLTIPS_CONSTANTS.RTS_ROSTER_SHELL, TOOLTIPS_CONSTANTS.RTS_ROSTER_MODULE, TOOLTIPS_CONSTANTS.RTS_CAROUSEL_VEHICLE]:
                intCD = event.getArgument('intCD')
                specialArgs = [intCD]
            if specialArgs is not None:
                return BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=specialAlias, specialArgs=specialArgs), self.getParentWindow())
            _logger.warning('[ROSTER_VIEW] Requested unsupported backport tooltip alias: %s', specialAlias)
            return

    @async
    def _onSave(self):
        _logger.debug('[ROSTER_VIEW] _onSave')
        yield await(self.__saveRoster(self._isModified, isForced=True))
        self.__handleClosing()

    @async
    def _onClose(self):
        _logger.debug('[ROSTER_VIEW] _onClose')
        shouldClose = yield await(self.__saveRoster(self._isModified, isForced=False))
        if shouldClose:
            self.__handleClosing()

    def _destroy(self):
        g_eventBus.handleEvent(CloseWindowEvent(CloseWindowEvent.RTS_ROSTER_CLOSED), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def _onCancelClicked(self):
        _logger.debug('[ROSTER_VIEW] _onCancelClicked')
        roster = self._itemsCache.items.aiRosters.getRosters().get(self.__battleType, {})
        self._mannersSettings.load(roster)
        with self.viewModel.transaction() as model:
            carousel = model.carousel
            self._buildCarouselModel(roster, carousel)
            self._invalidateGridManners(model.getVehicles())
            self._setIsModified(model, False)
        self._updateVehicleSpecsSelection()

    @args2params(int)
    def _onClearVehicleSlotClicked(self, slotIndex):
        _logger.debug('[ROSTER_VIEW] _onClearVehicleSlotClicked slot: %d', slotIndex)
        self._clearSlot(self.viewModel.carousel.getVehicleSlots(), slotIndex)

    @args2params(int)
    def _onClearSupplySlotClicked(self, slotIndex):
        _logger.debug('[ROSTER_VIEW] _onClearSupplySlotClicked slot: %d', slotIndex)
        self._clearSlot(self.viewModel.carousel.getSupplySlots(), slotIndex)

    def _clearSlot(self, slots, slotIndex):
        if slotIndex >= len(slots):
            _logger.error('Attempt to remove nonexisting slot!')
            return
        slots[slotIndex].setIsEmpty(True)
        self._setIsModified()
        self._updateVehicleSpecsSelection()

    def _setIsModified(self, model=None, isModified=True):
        if self._isModified == isModified:
            return
        self._isModified = isModified
        model = model if model else self.viewModel
        model.setHasConfigurationChanged(self._isModified)
        g_eventBus.handleEvent(events.FightButtonEvent(events.FightButtonEvent.FIGHT_BUTTON_UPDATE), EVENT_BUS_SCOPE.LOBBY)

    def _onFilterClearClicked(self):
        self._filter.reset()
        self.applyFilter()

    def _getRosterForSave(self):
        vehicles = self._getCurrentVehicleRoster()
        supplies = self._getCurrentSupplyRoster()
        manners = [ self._getManner(intCD) for intCD in vehicles ]
        _logger.debug('[ROSTER_VIEW] _getRosterForSave %s, %s, %s', vehicles, supplies, manners)
        return {'vehicles': vehicles,
         'supplies': supplies,
         'rtsManners': manners}

    @args2params(int)
    def _onItemClicked(self, intCD):
        _logger.debug('[ROSTER_VIEW] _onItemClicked')
        if self._isVehicleSelected():
            self._handleVehicleItemClicked(intCD)
        else:
            self._handleSupplyItemClicked(intCD)
        self._updateVehicleSpecsSelection()

    def _makeLevelKey(self, level):
        return 'level_%d' % level

    def _getCurrentVehicleRoster(self):
        return [ (slot.vehicle.getIntCD() if not slot.getIsEmpty() else 0) for slot in self.viewModel.carousel.getVehicleSlots() ]

    def _getCurrentSupplyRoster(self):
        return [ (slot.supply.getIntCD() if not slot.getIsEmpty() else 0) for slot in self.viewModel.carousel.getSupplySlots() ]

    def _getSlotCtx(self):
        if self._isVehicleSelected():
            config = self._rosterConfig['vehicles']['bots']
            selectedSlotIndex = self._selectedVehicleSlot
            imageGetter = partial(getIconShopResource, size=STORE_CONSTANTS.ICON_SIZE_SMALL)
            baseVehiclePacker = partial(packVehicleBaseModel, imageResGetter=imageGetter)
            rosterVehiclePacker = partial(packRosterVehicleModel, baseVehiclePacker=baseVehiclePacker, mannerGetter=self._getManner)
            vehicleConfig = config[selectedSlotIndex]
            ctx = {'slotIdx': selectedSlotIndex,
             'config': config,
             'criteria': getSuitableVehicleCriteriaForRoster(vehicleConfig),
             'modelPacker': rosterVehiclePacker,
             'modelClass': RosterVehicleViewModel,
             'allowedTags': vehicleConfig.get('allowedTags', frozenset())}
        else:
            config = self._rosterConfig.get('supplies', {}).get('types', {})
            tags = frozenset([ name for name in config.iterkeys() ])
            criteria = REQ_CRITERIA.VEHICLE.HAS_ANY_OF_TAGS(tags)
            rosterSupplyPacker = partial(fillRosterSupplyModel, supplyAmountSettings=self._getSupplyTypeToNumberInBattle())
            ctx = {'slotIdx': self._selectedSupplySlot,
             'config': config,
             'criteria': criteria,
             'modelPacker': rosterSupplyPacker,
             'modelClass': RosterSupplyViewModel,
             'allowedTags': frozenset()}
        return ctx

    def _isVehicleSelected(self):
        return self._selectedVehicleSlot is not self._UNSELECTED

    def _getManner(self, intCD):
        return self._mannersSettings.get(intCD, RTSManner.DEFAULT)

    def _handleSupplyItemClicked(self, vehicleIntCD):
        _logger.debug('[ROSTER_VIEW] _handleSupplyItemClicked')
        replaceIdx = -1
        isToggle = False
        roster = self._getCurrentSupplyRoster()
        selectedSlotIndex = self._selectedSupplySlot
        if vehicleIntCD in roster:
            if vehicleIntCD == roster[selectedSlotIndex]:
                isToggle = True
            else:
                replaceIdx = roster.index(vehicleIntCD)
        with self.viewModel.transaction() as model:
            self._setIsModified(model)
            slots = model.carousel.getSupplySlots()
            selectedSupplySlotModel = slots[selectedSlotIndex]
            if replaceIdx >= 0:
                replaceSlotModel = slots[replaceIdx]
                if selectedSupplySlotModel.getIsEmpty():
                    buildSupplySlotModel(vehicleIntCD, selectedSupplySlotModel, self._getSupplyTypeToNumberInBattle())
                    replaceSlotModel.setIsEmpty(True)
                    slots.invalidate()
                    return
                replaceSlotModel = slots[replaceIdx]
                swapSupplyModel(replaceSlotModel.supply, selectedSupplySlotModel.supply)
                return
            if isToggle:
                selectedSupplySlotModel.setIsEmpty(True)
                return
            buildSupplySlotModel(vehicleIntCD, selectedSupplySlotModel, self._getSupplyTypeToNumberInBattle())

    def _canMoveToSlot(self, originIdx, destIdx, slotsArray):
        slotClasses = self.viewModel.getSlotVehicleClasses()
        slotModel = slotsArray[originIdx]
        slotVehicle = self._slotCache[slotModel.vehicle.getIntCD()]
        return slotVehicle.tags.intersection(slotClasses[destIdx])

    def _handleVehicleItemClicked(self, vehicleIntCD):
        _logger.debug('[ROSTER_VIEW] _handleVehicleItemClicked')
        replaceIdx = -1
        isToggle = False
        roster = self._getCurrentVehicleRoster()
        selectedSlotIndex = self._selectedVehicleSlot
        if vehicleIntCD in roster:
            if vehicleIntCD == roster[selectedSlotIndex]:
                isToggle = True
            else:
                replaceIdx = roster.index(vehicleIntCD)
        with self.viewModel.transaction() as model:
            slots = model.carousel.getVehicleSlots()
            selectedVehicleSlotModel = slots[selectedSlotIndex]
            selectedVehicleModel = selectedVehicleSlotModel.vehicle
            if replaceIdx >= 0:
                replaceSlotModel = slots[replaceIdx]
                if not selectedVehicleSlotModel.getIsEmpty():
                    isSlotEmptyAfterSwapMap = {replaceIdx: not self._canMoveToSlot(originIdx=selectedSlotIndex, destIdx=replaceIdx, slotsArray=slots),
                     selectedSlotIndex: not self._canMoveToSlot(originIdx=replaceIdx, destIdx=selectedSlotIndex, slotsArray=slots)}
                    if all(isSlotEmptyAfterSwapMap.itervalues()):
                        return
                    self._setIsModified(model)
                    swapRosterVehicleViewModel(replaceSlotModel.vehicle, selectedVehicleModel)
                    if any(isSlotEmptyAfterSwapMap.itervalues()):
                        for idx, isEmpty in isSlotEmptyAfterSwapMap.iteritems():
                            slots[idx].setIsEmpty(isEmpty)

                    return
                else:
                    canMove = self._canMoveToSlot(originIdx=replaceIdx, destIdx=selectedSlotIndex, slotsArray=slots)
                    if canMove:
                        self._setIsModified(model)
                        buildVehicleSlotModel(vehicleIntCD, selectedVehicleSlotModel, self._getManner)
                        replaceSlotModel.setIsEmpty(True)
                        slots.invalidate()
                    return
            self._setIsModified(model)
            if isToggle:
                selectedVehicleSlotModel.setIsEmpty(True)
                return
            buildVehicleSlotModel(vehicleIntCD, selectedVehicleSlotModel, self._getManner)

    def _getVehicleIntCDForSlot(self, slotId):
        slots = self.viewModel.carousel.getVehicleSlots()
        slot = slots[slotId]
        return slot.vehicle.getIntCD() if slot is not None and not slot.getIsEmpty() else None

    def _getSupplyIntCDForSlot(self, slotId):
        slots = self.viewModel.carousel.getSupplySlots()
        slot = slots[slotId]
        return slot.supply.getIntCD() if slot is not None and not slot.getIsEmpty() else None

    @args2params(int)
    def _onVehicleSlotClicked(self, slotIndex):
        _logger.debug('[ROSTER_VIEW] _onVehicleSlotClicked')
        self._selectedVehicleSlot = slotIndex
        self._selectedSupplySlot = self._UNSELECTED
        with self.viewModel.transaction() as model:
            model.carousel.setSelectedSupplySlot(-1)
            model.carousel.setSelectedVehicleSlot(slotIndex)
            self._invalidateAll(model)
        self._updateVehicleSpecsSelection()

    @args2params(int)
    def _onSupplySlotClicked(self, slotIndex):
        _logger.debug('[ROSTER_VIEW] _onSupplySlotClicked')
        self._selectedVehicleSlot = self._UNSELECTED
        self._selectedSupplySlot = slotIndex
        with self.viewModel.transaction() as model:
            model.carousel.setSelectedSupplySlot(slotIndex)
            model.carousel.setSelectedVehicleSlot(-1)
            self._invalidateAll(model)
        self._updateVehicleSpecsSelection()

    def _getCurrentvehicles(self):
        return [ intCD for intCD in self._filteredIntCDs if self._filter.apply(self._slotCache[intCD]) ]

    def _getSlotSupportedTypes(self, idx):
        supportedTypesArray = self.viewModel.getSlotVehicleClasses()[idx]
        supportedTypes = [ i for i in supportedTypesArray ]
        return supportedTypes

    @args2params(int)
    def _onMannerClicked(self, manner):
        _logger.debug('[ROSTER_VIEW] onMannerClicked: %s', manner)
        if not self._isVehicleSelected():
            return
        else:
            slots = self.viewModel.carousel.getVehicleSlots()
            slot = slots[self._selectedVehicleSlot]
            if slot is None or slot.getIsEmpty():
                _logger.warning('[RosterView]: Attempt to set manner on empty slot. UI should not allow it.')
                return
            with self.viewModel.transaction() as model:
                self._setIsModified(model)
                intCD = slot.vehicle.getIntCD()
                slot.vehicle.setManner(MannerEnum(manner))
                slots.invalidate()
                self._mannersSettings[intCD] = manner
                vehicles = model.getVehicles()
                for vehicle in vehicles:
                    if vehicle.getIntCD() == intCD:
                        vehicle.setManner(MannerEnum(manner))
                        vehicles.invalidate()
                        return

            return

    @args2params(str)
    def _onFilterTextChanged(self, filterText):
        _logger.debug('[ROSTER_VIEW] _onFilterTextChanged: %s', filterText)
        self._filter.update({'searchNameVehicle': filterText}, save=False)
        self.applyFilter()

    def __onCacheResync(self, reason, diff):
        _logger.debug('[ROSTER_VIEW] _onCacheResync')
        if reason in (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.DOSSIER_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE) or GUI_ITEM_TYPE.VEHICLE in diff:
            with self.viewModel.transaction() as model:
                self._invalidateAll(model)

    def __onVehicleClientStateChanged(self, vehiclesIntCDs):
        _logger.debug('[ROSTER_VIEW] __onVehicleClientStateChanged')
        with self.viewModel.transaction() as model:
            self._invalidateAll(model)

    def __getCachedVehicle(self, vehicleIntCD):
        if vehicleIntCD in self._slotCache:
            return self._slotCache[vehicleIntCD]
        _logger.error('[RosterView] __getCachedVehicle cannot find vehicle: %s in _slotCache: %s', vehicleIntCD, self._slotCache.keys())

    @async
    def __closeConfirmation(self):
        _logger.debug('[ROSTER_VIEW] __closeConfirmation')
        result = AsyncReturn(True)
        if not self.__isClosed:
            shouldClose = yield await(self.__saveRoster(self._isModified, isForced=False))
            result = result if shouldClose else AsyncReturn(False)
            if shouldClose:
                g_eventBus.handleEvent(CloseWindowEvent(CloseWindowEvent.RTS_ROSTER_CLOSED), EVENT_BUS_SCOPE.LOBBY)
        raise result

    def __handleClosing(self):
        self.viewModel.setIsClosing(True)
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        return

    @async
    def __saveRoster(self, isChanged, isForced):
        _logger.debug('[ROSTER_VIEW] __saveRoster: %s %s', str(isChanged), str(isForced))
        shouldClose = True
        shouldSave = isChanged
        if shouldSave and not isForced:
            from gui.shared.event_dispatcher import showRTSRosterSaveDialog
            shouldSave, wasCanceled = yield await(showRTSRosterSaveDialog())
            shouldClose = not wasCanceled
        if shouldSave:
            roster = self._getRosterForSave()
            BigWorld.player().setAIRoster(self.__battleType, roster, _saveCallback)
        self._setIsModified(isModified=False)
        self.__isClosed = shouldClose
        raise AsyncReturn(shouldClose)

    def _updateVehicleSpecsSelection(self):
        if self._selectedVehicleSlot is not self._UNSELECTED:
            selectedIntCD = self._getVehicleIntCDForSlot(self._selectedVehicleSlot)
        elif self._selectedSupplySlot is not self._UNSELECTED:
            selectedIntCD = self._getSupplyIntCDForSlot(self._selectedSupplySlot)
        else:
            selectedIntCD = None
        self._vehicleSpecs.vehicleSelected(selectedIntCD)
        return

    def _updateGameModeValue(self):
        gameMode = getGameMode(self.__battleType)
        if gameMode:
            self.viewModel.setGameMode(gameMode)

    def _getSupplyTypeToNumberInBattle(self):
        return self._rosterConfig.get('supplies', {}).get('supplyTypeToNumberInBattle', {})

    def hasUnsavedChanges(self):
        return self._isModified


class RosterWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, layoutId, battleType, selectedSupplySlot=-1, selectedVehicleSlot=-1, parent=None):
        super(RosterWindow, self).__init__(WindowFlags.WINDOW, content=RosterView(layoutId, battleType, selectedSupplySlot, selectedVehicleSlot), parent=parent)
