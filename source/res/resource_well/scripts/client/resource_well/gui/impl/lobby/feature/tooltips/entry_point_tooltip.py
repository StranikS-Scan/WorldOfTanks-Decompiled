# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/tooltips/entry_point_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency, time_utils
from resource_well.gui.feature.constants import PurchaseMode
from resource_well.gui.feature.resource_well_helpers import isEventEndingsSoon, convertPurchaseToEventMode, hasRequiredStyle
from resource_well.gui.impl.gen.view_models.views.lobby.enums import EventMode
from resource_well.gui.impl.gen.view_models.views.lobby.tooltips.entry_point_tooltip_model import EntryPointTooltipModel, EventState
from resource_well.gui.impl.gen.view_models.views.lobby.tooltips.reward_info_model import RewardInfoModel, RewardState
from skeletons.gui.resource_well import IResourceWellController
_PurchaseModeToEventModeMap = {PurchaseMode.ONE_SERIAL_PRODUCT: EventMode.ONE_SERIAL_PRODUCT,
 PurchaseMode.SEQUENTIAL_PRODUCT: EventMode.SEQUENTIAL_PRODUCT,
 PurchaseMode.TWO_PARALLEL_PRODUCTS: EventMode.TWO_PARALLEL_PRODUCTS}

class EntryPointTooltip(ViewImpl):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.resource_well.lobby.feature.tooltips.EntryPointTooltip(), model=EntryPointTooltipModel())
        super(EntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPointTooltip, self)._onLoading(*args, **kwargs)
        self.__resourceWell.startNumberRequesters()
        with self.viewModel.transaction() as model:
            model.setEventMode(convertPurchaseToEventMode(self.__resourceWell.getPurchaseMode()))
            self.__fillEventState(model=model)
            self.__fillEventTime(model=model)
            self.__fillRewards(model=model)

    def _finalize(self):
        self.__resourceWell.stopNumberRequesters()
        super(EntryPointTooltip, self)._finalize()

    def _getEvents(self):
        return ((self.__resourceWell.onNumberRequesterUpdated, self.__fillRewards), (self.__resourceWell.onEventUpdated, self.__onEventUpdated), (self.__resourceWell.onSettingsChanged, self.__onSettingsChanged))

    @replaceNoneKwargsModel
    def __fillEventTime(self, model=None):
        config = self.__resourceWell.config
        isEventEnding = isEventEndingsSoon(resourceWell=self.__resourceWell)
        model.setEndDate(round(time_utils.makeLocalServerTime(config.finishTime), -1))
        model.setStartDate(round(time_utils.makeLocalServerTime(config.startTime), -1))
        model.setIsEventEndingSoon(isEventEnding)
        if isEventEnding:
            model.setTimeLeft(config.finishTime - time_utils.getServerUTCTime())

    @replaceNoneKwargsModel
    def __fillRewards(self, model=None):
        rewards = model.getRewards()
        rewards.clear()
        for rewardID, rewardConfig in self.__resourceWell.config.getSortedRewardsByOrder():
            vehicle = self.__resourceWell.getRewardVehicle(rewardID)
            rewardCount = self.__resourceWell.getRewardLeftCount(rewardID)
            rewardModel = RewardInfoModel()
            rewardModel.setRewardCount(rewardCount)
            rewardModel.setVehicleName(vehicle.shortUserName)
            rewardModel.setIsSerial(rewardConfig.isSerial)
            if self.__resourceWell.isRewardReceived(rewardID):
                state = RewardState.RECEIVED
            elif vehicle.isInInventory and hasRequiredStyle(rewardID, rewardConfig=rewardConfig):
                state = RewardState.IN_GARAGE
            elif rewardCount == 0:
                state = RewardState.SOLD_OUT
            else:
                state = RewardState.AVAILABLE
            rewardModel.setRewardState(state)
            rewards.addViewModel(rewardModel)

        rewards.invalidate()

    @replaceNoneKwargsModel
    def __fillEventState(self, model=None):
        if self.__resourceWell.isNotStarted():
            state = EventState.NOT_STARTED
        elif self.__resourceWell.isPaused():
            state = EventState.PAUSED
        elif self.__resourceWell.isForbiddenAccount():
            state = EventState.FORBIDDEN
        else:
            state = EventState.IN_PROGRESS
        model.setEventState(state)

    def __onEventUpdated(self):
        with self.viewModel.transaction() as model:
            self.__fillEventState(model=model)
            self.__fillEventTime(model=model)

    def __onSettingsChanged(self):
        with self.viewModel.transaction() as model:
            self.__fillEventState(model=model)
            self.__fillEventTime(model=model)
            self.__fillRewards(model=model)
