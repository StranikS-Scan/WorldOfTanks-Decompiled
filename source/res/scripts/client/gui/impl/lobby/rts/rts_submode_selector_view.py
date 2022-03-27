# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/rts_submode_selector_view.py
import logging
from typing import TYPE_CHECKING, Tuple
from adisp import process
from CurrentVehicle import g_currentVehicle
from account_helpers.client_ai_rosters import getSuitableVehiclesCriteria
from constants import ARENA_BONUS_TYPE
from frameworks.wulf import ViewSettings, ViewFlags, Array
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.rts_currency_view_model import CurrencyTypeEnum
from gui.impl.gen.view_models.views.lobby.rts.sub_mode_selector_view.rts_submode_selector_view_model import RtsSubmodeSelectorViewModel
from gui.impl.gen.view_models.views.lobby.rts.sub_mode_selector_view.sub_mode_tooltip_model import SubModeTooltipModel, SubModeStatus
from gui.impl.gen.view_models.views.lobby.rts.sub_mode_selector_view.submode_view_model import SubModesEnum, SubmodeViewModel, SubModeStateEnum
from gui.impl.lobby.rts.tooltips.tooltip_helpers import createRTSCurrencyTooltipView
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.rts_battles.rts_helpers import playedRandomBattleOnTierXVehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from gui.game_control.rts_battles_controller import RTSBattlesController
_logger = logging.getLogger(__name__)
SUB_MODE_ORDER = (SubModesEnum.STRATEGIST1X1, SubModesEnum.TANKER, SubModesEnum.STRATEGIST1X7)
SUB_MODE_TO_ARENA_TYPE = {SubModesEnum.STRATEGIST1X1: ARENA_BONUS_TYPE.RTS_1x1,
 SubModesEnum.STRATEGIST1X7: ARENA_BONUS_TYPE.RTS,
 SubModesEnum.TANKER: ARENA_BONUS_TYPE.RTS}
SUB_MODE_TO_CURRENCY_TYPE = {SubModesEnum.STRATEGIST1X1: CurrencyTypeEnum.CURRENCY1X1,
 SubModesEnum.STRATEGIST1X7: CurrencyTypeEnum.CURRENCY1X7}

class RTSSubModeSelectorView(ViewImpl):
    __slots__ = ('_currentSubMode', '_widget')
    __itemsCache = dependency.descriptor(IItemsCache)
    _rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.rts.SubModeSelectorView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = RtsSubmodeSelectorViewModel()
        super(RTSSubModeSelectorView, self).__init__(settings)
        self._currentSubMode = SubModesEnum.TANKER

    @property
    def viewModel(self):
        return super(RTSSubModeSelectorView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        _logger.debug('[RTS_SUBMODE_SELECTOR] createToolTipContent event %s, contentID %s', event, contentID)
        if contentID == R.views.lobby.rts.SubModeTooltip():
            subMode = SubModesEnum(event.getArgument('subMode', 'rtsTanker'))
            resource = R.strings.rts_battles.tooltip.submode.dyn(subMode.value)
            model = SubModeTooltipModel()
            model.setSectionText(backport.text(resource.sectionDescription()))
            model.setTitle(backport.text(resource.title()))
            model.setDescription(backport.text(resource.description()))
            status, reason = self._getAvailability(subMode)
            model.setStatus(status)
            model.setUnavailableReason(backport.text(reason))
            model.setDate(self._rtsController.getLockedEndDate())
            if subMode is not SubModesEnum.TANKER:
                arenaType = SUB_MODE_TO_ARENA_TYPE[subMode]
                subModePrice = self._rtsController.getSettings().currencyAmountToBattle(arenaType)
                model.currency.setCurrencyPrice(subModePrice)
                model.currency.setCurrencyType(SUB_MODE_TO_CURRENCY_TYPE[subMode])
                model.setSectionTitle(backport.text(resource.sectionTitle()))
            return ViewImpl(ViewSettings(contentID, model=model))
        elif contentID == R.views.lobby.rts.StrategistCurrencyTooltip():
            arg = event.getArgument('currencyType', None)
            return createRTSCurrencyTooltipView(contentID, arg)
        else:
            return super(RTSSubModeSelectorView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(RTSSubModeSelectorView, self)._initialize(*args, **kwargs)
        self.viewModel.onModeSelected += self._onModeSelected
        self._rtsController.onUpdated += self._onRTSUpdate

    def _onLoading(self, *args, **kwargs):
        super(RTSSubModeSelectorView, self)._onLoading(*args, **kwargs)
        self._buildSubModesArray(self.viewModel.getSubModes())
        self._onRTSUpdate()

    def _finalize(self):
        self.viewModel.onModeSelected -= self._onModeSelected
        self._rtsController.onUpdated -= self._onRTSUpdate
        super(RTSSubModeSelectorView, self)._finalize()

    def _isRosterComplete(self, bonusType):
        roster = self._rtsController.getRoster(bonusType)
        itemCDs = roster.vehicles + roster.supplies
        if not all(itemCDs):
            return False
        criteria = REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(itemCDs)
        rosterItems = self.__itemsCache.items.getVehicles(criteria).values()
        return False if len(itemCDs) != len(rosterItems) else True

    def _hasSuitableVehiclesForTanker(self):
        vehicleConfig = self._rtsController.getSettings().getVehicleRestrictions(ARENA_BONUS_TYPE.RTS)
        criteria = getSuitableVehiclesCriteria([vehicleConfig]) | REQ_CRITERIA.INVENTORY
        return any(self.__itemsCache.items.getVehicles(criteria).values())

    def _getCurrentSubMode(self):
        if self._rtsController.getBattleMode() == ARENA_BONUS_TYPE.RTS_1x1:
            return SubModesEnum.STRATEGIST1X1
        return SubModesEnum.TANKER if not self._rtsController.isCommander() else SubModesEnum.STRATEGIST1X7

    def _getAvailability(self, subMode):
        resource = R.strings.rts_battles.tooltip.submode
        submodeState, reason = self._getSubmodeState(subMode)
        if submodeState in (SubModeStateEnum.LOCKED, SubModeStateEnum.UNAVAILABLE):
            return (submodeState, reason)
        arenaType = SUB_MODE_TO_ARENA_TYPE[subMode]
        isTanker = subMode is SubModesEnum.TANKER
        hasEnoughCurrency = self._rtsController.hasEnoughCurrency(arenaType) or isTanker
        if not hasEnoughCurrency:
            return (SubModeStatus.UNAVAILABLE, resource.dyn(subMode.value).not_enough_currency())
        if not playedRandomBattleOnTierXVehicle(self.__itemsCache, self._rtsController):
            return (SubModeStatus.UNAVAILABLE, resource.no_tier_x_battle())
        if isTanker:
            if not self._hasSuitableVehiclesForTanker():
                return (SubModeStatus.UNAVAILABLE, resource.no_suitable_vehicles())
            if not g_currentVehicle.isReadyToFight():
                return (SubModeStatus.UNAVAILABLE, resource.not_ready_for_battle())
            if g_currentVehicle.isPresent() and not g_currentVehicle.item.isAmmoFull:
                return (SubModeStatus.UNAVAILABLE, resource.not_ready_for_battle())
            if g_currentVehicle.isUnsuitableToQueue():
                return (SubModeStatus.UNAVAILABLE, resource.unsuitable_vehicle_selected())
        elif not self._isRosterComplete(arenaType):
            return (SubModeStatus.UNAVAILABLE, resource.roster_incomplete())
        return (SubModeStatus.FREE, R.invalid()) if submodeState == SubModeStateEnum.FREE else (SubModeStatus.AVAILABLE, resource.ready_for_battle())

    def _fillCurrencyModel(self, model, subMode, arenaType):
        currencyModel = model.currency
        currencyModel.setCurrencyValue(self._rtsController.getCurrency(arenaType))
        currencyModel.setCurrencyPrice(self._rtsController.getSettings().currencyAmountToBattle(arenaType, ignoreWarmup=True))
        currencyModel.setCurrencyType(SUB_MODE_TO_CURRENCY_TYPE[subMode])

    def _fillSubModeModel(self, subModeModel, subMode):
        subModeModel.setSubMode(subMode)
        submodeState, _ = self._getSubmodeState(subMode)
        subModeModel.setState(submodeState)
        subModeModel.setDate(self._rtsController.getLockedEndDate())
        if subMode is not SubModesEnum.TANKER:
            arenaType = SUB_MODE_TO_ARENA_TYPE[subMode]
            self._fillCurrencyModel(subModeModel, subMode, arenaType)

    def _getSubmodeState(self, subMode):
        rtsController = self._rtsController
        settings = rtsController.getSettings()
        bonusType = SUB_MODE_TO_ARENA_TYPE[subMode]
        isEnabled = settings.isSubmodeEnabled(bonusType)
        if not isEnabled:
            if rtsController.getLockedEndDate():
                return (SubModeStateEnum.LOCKED, R.invalid())
            return (SubModeStateEnum.UNAVAILABLE, R.strings.rts_battles.subModeSelector.killSwitch())
        return (SubModeStateEnum.FREE, R.invalid()) if settings.isWarmupEnabled() else (SubModeStateEnum.NORMAL, R.invalid())

    def _buildSubModesArray(self, array):
        if array:
            _logger.error('[RTS_SUBMODE_SELECTOR] Submodes array already initialized!')
        array.reserve(len(SubModesEnum))
        for subMode in SUB_MODE_ORDER:
            subModeModel = SubmodeViewModel()
            subModeModel.setSubMode(subMode)
            array.addViewModel(subModeModel)

    def _fillSubModesArray(self, array):
        for subModeModel in array:
            self._fillSubModeModel(subModeModel, subModeModel.getSubMode())

    def _onRTSUpdate(self, *_):
        _logger.debug('[RTS_SUBMODE_SELECTOR] _onRTSUpdate')
        self._currentSubMode = self._getCurrentSubMode()
        with self.viewModel.transaction() as model:
            model.setCurrentSubMode(self._currentSubMode.value)
            self._fillSubModesArray(model.getSubModes())

    def _getPrbData(self, subMode):
        return PREBATTLE_ACTION_NAME.RTS_1x1 if subMode is SubModesEnum.STRATEGIST1X1 else PREBATTLE_ACTION_NAME.RTS

    @process
    def _switchPrbEntity(self, subMode):
        _logger.debug('[RTS_SUBMODE_SELECTOR] _doSelect changing prbEntity %s', subMode)
        dispatcher = self._rtsController.prbDispatcher
        yield dispatcher.doSelectAction(PrbAction(self._getPrbData(subMode)))

    @args2params(str)
    def _onModeSelected(self, subMode):
        _logger.debug('[RTS_SUBMODE_SELECTOR] _onModeSelected selected %s', subMode)
        subMode = SubModesEnum(subMode)
        if subMode is self._currentSubMode:
            return
        self._currentSubMode = subMode
        bonusType = SUB_MODE_TO_ARENA_TYPE[subMode]
        if bonusType != self._rtsController.getBattleMode():
            self._switchPrbEntity(subMode)
        if self._rtsController.isTankistEnabled():
            isCommander = subMode is not SubModesEnum.TANKER
            self._rtsController.changeControlMode(isCommander=isCommander)
