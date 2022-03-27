# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/carousel_view.py
import logging
import BigWorld
from Event import Event
from frameworks.wulf import ViewFlags, ViewSettings, Array, WindowStatus
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.carousel_supply_slot_model import CarouselSupplySlotModel
from gui.impl.gen.view_models.views.lobby.rts.carousel_vehicle_slot_model import CarouselVehicleSlotModel
from gui.impl.gen.view_models.views.lobby.rts.carousel_view_model import CarouselViewModel, StateEnum
from gui.impl.gen.view_models.views.lobby.rts.roster_view.supply_details_tooltip_model import SupplyDetailsTooltipModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.rts.model_helpers import buildVehicleSlotModel, buildSupplySlotModel
from gui.impl.lobby.rts.rts_roster_view import RosterWindow
from gui.impl.lobby.rts.vehicle_specs.rts_vehicle_builder import RtsVehicleBuilder
from gui.impl.lobby.rts.vehicle_specs.rts_vehicle_parameters import RtsVehicleParameters
from gui.impl.pub import ViewImpl
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)
_DEFAULT_VEHICLE_ARRAY = [0] * 7
_DEFAULT_SUPPLY_ARRAY = [0] * 3
_NUM_OF_SUPPLY_SLOTS = 3

class VignetteHolder(object):
    __slots__ = ('__defaultIntensity',)
    _VIGNETTE_INTENSITY = 0.85

    def __init__(self):
        vignetteSettings = BigWorld.WGRenderSettings().getVignetteSettings()
        self.__defaultIntensity = vignetteSettings.w
        vignetteSettings[3] = self._VIGNETTE_INTENSITY
        BigWorld.WGRenderSettings().setVignetteSettings(vignetteSettings)

    def __del__(self):
        vignetteSettings = BigWorld.WGRenderSettings().getVignetteSettings()
        vignetteSettings[3] = self.__defaultIntensity
        BigWorld.WGRenderSettings().setVignetteSettings(vignetteSettings)


class CarouselView(ViewImpl):
    __slots__ = ('__vignette', '_mode', '_roster', '_rosterConfig', '_vehicleSlotSizes', '_supplySlotSizes', '_selectedSupplySlot', '_selectedVehicleSlot', 'onSlotSelected')
    _rtsController = dependency.descriptor(IRTSBattlesController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _gui = dependency.descriptor(IGuiLoader)
    _UNSELECTED = -1

    def __init__(self):
        _logger.debug('[STRATEGIST CAROUSEL] ctor')
        settings = ViewSettings(R.views.lobby.rts.CarouselView(), ViewFlags.COMPONENT, CarouselViewModel())
        super(CarouselView, self).__init__(settings)
        self.__vignette = None
        self._mode = self._rtsController.getBattleMode()
        self._roster = None
        self._rosterConfig = None
        self._selectedSupplySlot = self._UNSELECTED
        self._selectedVehicleSlot = self._UNSELECTED
        self.onSlotSelected = Event()
        _logger.debug('[STRATEGIST CAROUSEL] get roster %s', self._roster)
        return

    @property
    def viewModel(self):
        return super(CarouselView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            window = self._createBackportTooltip(event)
            if window:
                window.load()
            return window
        return super(CarouselView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.rts.SupplyDetailsTooltip():
            supplyType = event.getArgument('type')
            intCD = int(event.getArgument('intCD'))
            model = SupplyDetailsTooltipModel()
            model.setType(supplyType)
            supply = RtsVehicleBuilder().createVehicle(intCD)
            RtsVehicleParameters(model.parameters).setVehicle(supply, forceUpdate=True)
            return ViewImpl(ViewSettings(contentID, model=model))
        return super(CarouselView, self).createToolTipContent(event=event, contentID=contentID)

    def _createBackportTooltip(self, event):
        if not event.hasArgument('specialAlias'):
            _logger.warning('[CAROUSEL_VIEW] Requested backport tooltip but specialAlias is missing!')
            return None
        else:
            specialAlias = event.getArgument('specialAlias')
            if specialAlias == TOOLTIPS_CONSTANTS.RTS_VEHICLE_PARAMETERS:
                parameterName = event.getArgument('name')
                specialArgs = [parameterName]
            elif specialAlias == TOOLTIPS_CONSTANTS.RTS_CAROUSEL_VEHICLE:
                intCD = event.getArgument('intCD')
                specialArgs = [intCD]
            else:
                _logger.warning('[CAROUSEL_VIEW] Requested unsupported backport tooltip alias: %s', specialAlias)
                return None
            return BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=specialAlias, specialArgs=specialArgs), self.getParentWindow())

    def _initialize(self, *args, **kwargs):
        self._rtsController.onUpdated += self._onRtsControllerUpdated
        self._rtsController.onRosterUpdated += self._onRtsRosterUpdated
        self.viewModel.onSupplySlotClicked += self._onSupplySlotClicked
        self.viewModel.onVehicleSlotClicked += self._onVehicleSlotClicked
        self.viewModel.onHidingAnimationEnded += self._onHidingAnimationEnded

    def _finalize(self):
        self.__vignette = None
        self._rtsController.onUpdated -= self._onRtsControllerUpdated
        self._rtsController.onRosterUpdated -= self._onRtsRosterUpdated
        self.viewModel.onSupplySlotClicked -= self._onSupplySlotClicked
        self.viewModel.onVehicleSlotClicked -= self._onVehicleSlotClicked
        self.viewModel.onHidingAnimationEnded -= self._onHidingAnimationEnded
        self.onSlotSelected.clear()
        return

    def _onLoading(self, *args, **kwargs):
        self.__vignette = VignetteHolder()
        self._updateRosterConfig()
        self._fillCarouselModel()

    def _fillCarouselModel(self):
        with self.viewModel.transaction() as model:
            self._fillVehicleSlots(model.getVehicleSlots())
            self._fillSupplySlots(model.getSupplySlots())

    def _fillSupplySlots(self, slotArray):
        arraySize = self._rosterConfig.get('supplies', {}).get('slots', 0)
        slotArray.clear()
        slotArray.reserve(arraySize)
        supplyTypeToNumberInBattle = self._rosterConfig.get('supplies', {}).get('supplyTypeToNumberInBattle', {})
        roster = self._roster.supplies
        rosterSize = len(roster)
        for slotIndex in range(arraySize):
            slotModel = CarouselSupplySlotModel()
            if slotIndex < rosterSize:
                buildSupplySlotModel(roster[slotIndex], slotModel, supplyTypeToNumberInBattle)
            slotArray.addViewModel(slotModel)

        slotArray.invalidate()

    def _fillVehicleSlots(self, slotArray):
        arraySize = self._rosterConfig.get('vehicles', {}).get('slots', 0)
        slotArray.clear()
        slotArray.reserve(arraySize)
        roster = self._roster.vehicles
        rosterSize = len(roster)
        for slotIndex in range(arraySize):
            slotModel = CarouselVehicleSlotModel()
            if slotIndex < rosterSize:
                buildVehicleSlotModel(roster[slotIndex], slotModel)
            slotArray.addViewModel(slotModel)

        slotArray.invalidate()

    def _updateRosterConfig(self):
        self._roster = self._rtsController.getRoster(self._mode)
        self._rosterConfig = self._lobbyContext.getServerSettings().getAIRostersConfig().get(self._mode, {})

    def _onRtsRosterUpdated(self, _):
        self._updateRosterConfig()
        self._fillCarouselModel()

    def _onRtsControllerUpdated(self):
        _logger.debug('[STRATEGIST CAROUSEL] _onRtsControllerUpdated')
        self._mode = self._rtsController.getBattleMode()
        self._updateRosterConfig()
        self._fillCarouselModel()

    def _openRosterView(self):
        layoutID = R.views.lobby.rts.RosterView()
        currentView = self._gui.windowsManager.getViewByLayoutID(layoutID)
        if currentView is None:
            w = RosterWindow(layoutID, self._mode, self._selectedSupplySlot, self._selectedVehicleSlot, self.getParentWindow())
            w.content.onStatusChanged += self._onStatusChangedRoster
            w.load()
        return

    @args2params(int)
    def _onVehicleSlotClicked(self, slotIndex):
        _logger.debug('[STRATEGIST CAROUSEL] _onVehicleSlotClicked')
        self._onSlotSelected(selectedVehicleSlot=slotIndex, selectedSupplySlot=self._UNSELECTED)

    @args2params(int)
    def _onSupplySlotClicked(self, slotIndex):
        _logger.debug('[STRATEGIST CAROUSEL] _onSupplySlotClicked')
        self._onSlotSelected(selectedVehicleSlot=-1, selectedSupplySlot=slotIndex)

    def _onSlotSelected(self, selectedVehicleSlot, selectedSupplySlot):
        self._selectedVehicleSlot = selectedVehicleSlot
        self._selectedSupplySlot = selectedSupplySlot
        self.viewModel.setState(StateEnum.HIDING)
        self.onSlotSelected()

    def _onHidingAnimationEnded(self):
        self._openRosterView()

    def _onStatusChangedRoster(self, windowStatus):
        if windowStatus == WindowStatus.LOADED:
            self.viewModel.setState(StateEnum.HIDDEN)
