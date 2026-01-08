# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/tooltips/event_banner_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency, time_utils
from resource_well.gui.impl.gen.view_models.views.lobby.tooltips.event_banner_tooltip_model import EventBannerTooltipModel
from resource_well.gui.impl.gen.view_models.views.lobby.tooltips.reward_info_model import RewardInfoModel
from skeletons.gui.resource_well import IResourceWellController

class EventBannerTooltip(ViewImpl):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.resource_well.mono.lobby.tooltips.event_banner_tooltip(), model=EventBannerTooltipModel())
        super(EventBannerTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventBannerTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self.__resourceWell.onEventUpdated, self.__onEventUpdated), (self.__resourceWell.onSettingsChanged, self.__onSettingsChanged))

    def _onLoading(self, *args, **kwargs):
        super(EventBannerTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__fillEventState(model=model)
            self.__fillEventTime(model=model)
            self.__fillRewards(model=model)

    @replaceNoneKwargsModel
    def __fillEventTime(self, model=None):
        config = self.__resourceWell.config
        model.setStartDate(config.startTime)
        model.setEndDate(config.finishTime)

    @replaceNoneKwargsModel
    def __fillRewards(self, model=None):
        rewards = model.getRewards()
        rewards.clear()
        for rewardID, _ in self.__resourceWell.config.getSortedRewardsByOrder():
            vehicle = self.__resourceWell.getRewardVehicle(rewardID)
            if vehicle is not None:
                rewardModel = RewardInfoModel()
                rewardModel.setVehicleName(vehicle.shortUserName)
                rewards.addViewModel(rewardModel)

        rewards.invalidate()
        return

    @replaceNoneKwargsModel
    def __fillEventState(self, model=None):
        if self.__resourceWell.isNotStarted() and not self.__resourceWell.isActive():
            timeBeforeStart = self.__resourceWell.config.startTime - time_utils.getServerUTCTime()
            if timeBeforeStart > time_utils.ONE_DAY:
                model.setState(EventBannerState.ANNOUNCE)
            else:
                model.setState(EventBannerState.INACTIVE)
        else:
            model.setState(EventBannerState.IN_PROGRESS)

    def __onEventUpdated(self):
        with self.viewModel.transaction() as model:
            self.__fillEventState(model=model)
            self.__fillEventTime(model=model)
            self.__fillRewards(model=model)

    def __onSettingsChanged(self):
        with self.viewModel.transaction() as model:
            self.__fillEventState(model=model)
            self.__fillEventTime(model=model)
            self.__fillRewards(model=model)
