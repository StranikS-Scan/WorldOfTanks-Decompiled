# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_awards_vehicles_view.py
from __future__ import absolute_import
import logging
import typing
import BigWorld
from BWUtil import AsyncReturn
from constants import ROLE_TYPE
from frameworks.wulf import ViewSettings, WindowLayer
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.game_control.seniority_awards_controller import VehicleSelectionState, VehiclesForSelectionState, SELECT_REWARD_TIMEOUT
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent, getSeniorityAwardsVehicles
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_tooltip_constants import SeniorityAwardsTooltipConstants
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_vehicle_model import SeniorityAwardsVehicleModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_vehicles_view_model import SeniorityAwardsVehiclesViewModel, ViewState
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.platoon.platoon_helpers import removeNationFromTechName
from gui.impl.lobby.seniority_awards.seniority_awards_helper import getVehicleCD, showVehicleSelectionTimeoutError, showVehicleSelectionMultipleTokensError, getRewardCategoryForUI
from gui.impl.lobby.seniority_awards.seniority_awards_sounds import SENIORITY_REWARD_SOUND_SPACE
from gui.impl.lobby.seniority_awards.tooltip.seniority_awards_tooltip import SeniorityAwardsTooltip
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import event_dispatcher
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.gui.game_control import ISeniorityAwardsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from uilogging.seniority_awards.loggers import VehicleSelectionErrorNotificationsLogger
from wg_async import wg_async, wg_await, BrokenPromiseError, AsyncScope, AsyncEvent, TimeoutError
_logger = logging.getLogger(__name__)
_SENIORITY_VEHICLES_ORDER = ('uk:GB156_Black_Prince_II',
 'uk:GB146_Gabler_s_Destroyer',
 'germany:G170_PzKpfwIV_Ausf_F2',
 'ussr:R197_KV_1S_MZ',
 'germany:G158_VK2801_105_SPXXI',
 'usa:A134_M24E2_SuperChaffee',
 'usa:A130_Super_Hellcat',
 'ussr:R160_T_50_2')

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _vehiclesSortOrder(vehicleCD, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(vehicleCD)
    return _SENIORITY_VEHICLES_ORDER.index(vehicle.name) if vehicle and vehicle.name in _SENIORITY_VEHICLES_ORDER else len(_SENIORITY_VEHICLES_ORDER)


def _sortVehiclesDict(vehDictItem):
    return _vehiclesSortOrder(vehDictItem[1].intCD)


class SeniorityRewardVehiclesView(ViewImpl):
    _COMMON_SOUND_SPACE = SENIORITY_REWARD_SOUND_SPACE
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __seniorityAwardsCtrl = dependency.descriptor(ISeniorityAwardsController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, contentResId, *args, **kwargs):
        settings = ViewSettings(layoutID=contentResId, model=SeniorityAwardsVehiclesViewModel(), args=args, kwargs=kwargs)
        super(SeniorityRewardVehiclesView, self).__init__(settings)
        self.__vehicles = []
        self.__selectedVehicleId = ''
        self.__state = None
        self.__scope = AsyncScope()
        self.__vehicleSelectionQuestCompletedEvent = AsyncEvent(scope=self.__scope)
        self.__vehicleSelectionQuestId = ''
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @wg_async
    def __selectVehicleReward(self, vehicleRewardId):
        if self.__seniorityAwardsCtrl.isVehicleSelectionAvailable:
            self.__vehicleSelectionQuestId = vehicleRewardId
            token = self.__seniorityAwardsCtrl.claimVehicleRewardTokenPattern.format(id=vehicleRewardId)
            BigWorld.player().requestSingleToken(token)
            try:
                try:
                    yield wg_await(self.__vehicleSelectionQuestCompletedEvent.wait(), timeout=SELECT_REWARD_TIMEOUT)
                    result = VehicleSelectionState.RECIEVED
                except TimeoutError:
                    result = VehicleSelectionState.SELECTION_FAILED
                except BrokenPromiseError:
                    _logger.debug('%s has been destroyed before %s completed', self, self.__seniorityAwardsCtrl.vehicleSelectionQuestPattern.format(id=self.__vehicleSelectionQuestId))
                    result = VehicleSelectionState.SELECTION_FAILED

            finally:
                self.__vehicleSelectionQuestId = ''

        else:
            result = VehicleSelectionState.HAS_CLIENT_TOKENS
        raise AsyncReturn(result)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SeniorityRewardVehiclesView, self).createToolTip(event)

    def getTooltipData(self, event):
        return self.__getBackportTooltipData(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView():
            vehicleCD = getVehicleCD(event.getArgument('vehicleCD'))
            if vehicleCD:
                return VehicleRolesTooltipView(vehicleCD)
            _logger.warning('Parameter vehicleCD is missing')
        return SeniorityAwardsTooltip(str(self.viewModel.getCategory()), self.viewModel.getMaxCategory(), self.__seniorityAwardsCtrl.yearsInGame) if contentID == R.views.mono.seniority_awards.tooltips.seniority_tooltip() else getRewardTooltipContent(event, self.__getBackportTooltipData(event))

    def _onLoading(self, vehicles, fromEntryPoint, *args, **kwargs):
        super(SeniorityRewardVehiclesView, self)._onLoading(*args, **kwargs)
        if not self.__seniorityAwardsCtrl.isVehicleSelectionAvailable and not vehicles:
            _logger.error('Wrong data to show view')
            return
        with self.viewModel.transaction() as vm:
            category = getRewardCategoryForUI()
            vm.setCategory(category.lower())
            vm.setMaxCategory(self.__seniorityAwardsCtrl.maxCategory)
            vm.setFromEntryPoint(fromEntryPoint)
            if self.__seniorityAwardsCtrl.isVehicleSelectionAvailable:
                self.__state = ViewState.SELECTION
                self.__setAvailableVehicles(vm)
                vm.setAvailableRewardsCount(self.__seniorityAwardsCtrl.getVehiclesForSelectionCount)
            else:
                self.__state = ViewState.VIEW_REWARD
                self.__updateVehicles(vehicles)
                self.__setRewards(vm)
            vm.setViewState(self.__state)

    def _getEvents(self):
        return ((self.viewModel.onMoreRewards, self.__handleOnMoreRewards),
         (self.viewModel.onGoToHangar, self.__handleShowHangar),
         (self.viewModel.onClose, self.__handleOnClose),
         (self.viewModel.onSelectVehicleReward, self.__handleOnSelectVehicleReward),
         (self.__seniorityAwardsCtrl.onUpdated, self.__onSettingsChange),
         (self.__seniorityAwardsCtrl.onVehicleSelectionChanged, self.__onVehicleSelectionChanged),
         (self.__seniorityAwardsCtrl.onQuestsReceived, self.__onQuestsReceived))

    def _finalize(self):
        self.__vehicles = []
        self.__selectedVehicleId = ''
        self.__vehicleSelectionQuestCompletedEvent.clear()
        self.__scope.destroy()
        super(SeniorityRewardVehiclesView, self)._finalize()

    def __onQuestsReceived(self, *_, **__):
        if self.__vehicleSelectionQuestId and not self.__vehicleSelectionQuestCompletedEvent.is_set() and self.__seniorityAwardsCtrl.isVehicleSelectionQuestCompleted(self.__vehicleSelectionQuestId):
            self.__vehicleSelectionQuestCompletedEvent.set()

    def __setRewards(self, viewModel):
        vehiclesList = viewModel.getVehicles()
        vehiclesList.clear()
        for vehicleCD in self.__vehicles:
            vehicleItem = self.__itemsCache.items.getItemByCD(vehicleCD)
            vehicleModel = SeniorityAwardsVehicleModel()
            fillVehicleModel(vehicleModel, vehicleItem)
            vehicleModel.setRole(vehicleItem.role)
            vehiclesList.addViewModel(vehicleModel)

        vehiclesList.invalidate()

    def __setAvailableVehicles(self, viewModel):
        vehiclesList = viewModel.getVehicles()
        vehiclesList.clear()
        availableVehicles = sorted(self.__seniorityAwardsCtrl.getAvailableVehicleSelectionRewards().items(), key=_sortVehiclesDict)
        for vehicleId, vehicle in availableVehicles:
            vehicleModel = SeniorityAwardsVehicleModel()
            fillVehicleModel(vehicleModel, vehicle)
            if vehicle.role == ROLE_TYPE.NOT_DEFINED:
                vehicleModel.setRoleKey('')
            vehName = removeNationFromTechName(vehicle.name)
            vehicleModel.setDescription(backport.text(R.strings.seniority_awards.vehicle.dyn(vehName)()))
            vehicleModel.setVehicleId(vehicleId)
            vehicleModel.setRole(vehicle.role)
            vehiclesList.addViewModel(vehicleModel)

        vehiclesList.invalidate()

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            vehicleCD = getVehicleCD(event.getArgument('vehicleCD'))
            if vehicleCD is None:
                return
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SENIORITY_AWARD_VEHICLE, specialArgs=(vehicleCD,
             100,
             None,
             None,
             None,
             None,
             None,
             False,
             True,
             True,
             False)) if tooltipId == SeniorityAwardsTooltipConstants.TOOLTIP_VEHICLE_REWARD else None

    def __updateVehicles(self, vehicles):
        self.__vehicles = getSeniorityAwardsVehicles(vehicles, sortKey=_vehiclesSortOrder)

    def __handleOnMoreRewards(self):
        if self.__state in (ViewState.VIEW_REWARD, ViewState.VIEW_REWARD_AFTER_SELECTION):
            self.destroyWindow()
        else:
            _logger.error('MoreRewardsBtnClick was called with invalid state - %s', self.__state)

    def __handleShowHangar(self):
        if self.__state == ViewState.VIEW_REWARD_AFTER_SELECTION:
            if self.__vehicles:
                event_dispatcher.selectVehicleInHangar(self.__vehicles[0])
            else:
                _logger.error("Can't find vehicle to show")
            self.destroyWindow()
        else:
            _logger.error('ShowHangar was called with invalid state - %s', self.__state)

    @wg_async
    def __handleOnSelectVehicleReward(self, event):
        if self.__state == ViewState.SELECTION:
            self.__selectedVehicleId = event.get('selectedId', '')
            if not self.__selectedVehicleId:
                _logger.error("Invalid selected vehicleId: '%s'", self.__selectedVehicleId)
                self.destroyWindow()
                return
            self.__showWaiting()
            result = yield wg_await(self.__selectVehicleReward(self.__selectedVehicleId))
            if result == VehicleSelectionState.RECIEVED:
                self.__state = ViewState.VIEW_REWARD_AFTER_SELECTION
                vehicle = self.__seniorityAwardsCtrl.getVehicleSelectionQuestReward(self.__selectedVehicleId)
                if vehicle:
                    self.__vehicles = [vehicle.intCD]
                    self.__updateModelAfterSelection()
                else:
                    self.destroyWindow()
                    _logger.error('Cannot find recieved reward vehicle')
            elif result == VehicleSelectionState.SELECTION_FAILED:
                showVehicleSelectionTimeoutError()
                VehicleSelectionErrorNotificationsLogger().handleTimeoutError()
                self.destroyWindow()
            elif result == VehicleSelectionState.HAS_CLIENT_TOKENS:
                showVehicleSelectionMultipleTokensError()
                VehicleSelectionErrorNotificationsLogger().handleMultipleTokensError()
                self.destroyWindow()
            self.__hideWaiting()
        else:
            _logger.error("SelectVehicleRewardBtnClick was called with invalid state: '%s'", self.__state)

    def __handleOnClose(self):
        self.destroyWindow()

    @staticmethod
    def __showWaiting():
        Waiting.show('selectSeniorityAwards')

    @staticmethod
    def __hideWaiting():
        Waiting.hide('selectSeniorityAwards')

    def __updateModelAfterSelection(self):
        with self.getViewModel().transaction() as vm:
            self.__setRewards(vm)
            vm.setViewState(self.__state)

    def __onSettingsChange(self):
        if self.__state == ViewState.SELECTION and (not self.__seniorityAwardsCtrl.isAvailable or not self.__seniorityAwardsCtrl.isVehicleSelectionAvailable):
            self.destroyWindow()

    def __onVehicleForSelectionChanged(self):
        if self.__state == ViewState.SELECTION:
            with self.viewModel.transaction() as vm:
                self.__setAvailableVehicles(vm)
                vm.setAvailableRewardsCount(self.__seniorityAwardsCtrl.getVehiclesForSelectionCount)

    def __onVehicleSelectionChanged(self, state):
        if state == VehiclesForSelectionState.STATE_CHANGED:
            return self.__onSettingsChange()
        if state == VehiclesForSelectionState.VEHICLES_CHANGED:
            return self.__onVehicleForSelectionChanged()
        _logger.error('Vehicle selection state is undefined %s', state)


class SeniorityRewardVehiclesWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, viewID=None, vehicles=None, fromEntryPoint=True):
        super(SeniorityRewardVehiclesWindow, self).__init__(content=SeniorityRewardVehiclesView(viewID, vehicles=vehicles, fromEntryPoint=fromEntryPoint), layer=WindowLayer.TOP_WINDOW)
