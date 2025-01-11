# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pm_announce/tooltips/personal_missions_new_campaign_tooltip_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_new_campaign_tooltip_view_model import PersonalMissionsNewCampaignTooltipViewModel, MissionStatus
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_old_campaign_tooltip_rewards_model import PersonalMissionsOldCampaignTooltipRewardsModel, RewardStatus
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_old_campaign_tooltip_operations_model import PersonalMissionsOldCampaignTooltipOperationsModel
from gui.impl.lobby.pm_announce.tooltips import getRewardStatusForOperation
from gui.impl.pub import ViewImpl
from helpers import dependency
from personal_missions import PM_BRANCH
from skeletons.gui.server_events import IEventsCache
LAST_REWARD = (backport.text(R.strings.pm_announce.newTooltip.vehicles.last()), 'R.images.gui.maps.icons.pm_announce.tooltips.new.hidden', RewardStatus.LOCKED)

class PersonalMissionsNewCampaignTooltipView(ViewImpl):
    __slots__ = ()
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PersonalMissionsNewCampaignTooltipViewModel()
        super(PersonalMissionsNewCampaignTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalMissionsNewCampaignTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsNewCampaignTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    def __updateModel(self, model):
        operations = self.__eventsCache.getPersonalMissions().getOperationsForBranch(PM_BRANCH.PERSONAL_MISSION_3)
        array = model.getOperations()
        rewardsArray = model.getRewards()
        isFullCompleted = all((operation.isFullCompleted() for operation in operations.itervalues()))
        isCompleted = all((operation.isCompleted() for operation in operations.itervalues()))
        for operation in operations.itervalues():
            questCount = len(operation.getQuestsByFilter(lambda q: q.isFinal())) if isCompleted else operation.getQuestsCount()
            completedQuestsCount = len(operation.getQuestsByFilter(lambda q: q.isFinal() and q.isFullCompleted()) if isCompleted else operation.getCompletedQuests())
            nextModel = PersonalMissionsOldCampaignTooltipOperationsModel()
            nextModel.setName(operation.getShortUserName())
            nextModel.setCompleted(completedQuestsCount)
            nextModel.setAll(questCount)
            array.addViewModel(nextModel)
            vehicle = operation.getVehicleBonus()
            rewardModel = PersonalMissionsOldCampaignTooltipRewardsModel()
            if vehicle is not None:
                rewardModel.setName(vehicle.userName)
                rewardModel.setIcon(vehicle.iconBonus)
            rewardModel.setStatus(getRewardStatusForOperation(operation))
            rewardsArray.addViewModel(rewardModel)

        if not isFullCompleted:
            rewardModel = PersonalMissionsOldCampaignTooltipRewardsModel()
            vehicleName, icon, status = LAST_REWARD
            rewardModel.setName(vehicleName)
            rewardModel.setIcon(icon)
            rewardModel.setStatus(status)
            rewardsArray.addViewModel(rewardModel)
        array.invalidate()
        if isCompleted and isFullCompleted:
            model.setMissionStatus(MissionStatus.COMPLETEDPERFECT)
            rewardsArray.clear()
        elif isCompleted:
            model.setMissionStatus(MissionStatus.COMPLETED)
            rewardsArray.invalidate()
        else:
            model.setMissionStatus(MissionStatus.ACTIVE)
            rewardsArray.invalidate()
        return
